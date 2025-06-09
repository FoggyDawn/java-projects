import time
import argparse
import subprocess
import psutil
import csv
from pathlib import Path
from datetime import datetime

# ==================== 用户配置区 ====================
JAVA_VERSIONS = {
    "8": "/home/byx/.jdks/corretto-1.8.0_442/bin/java",    # Java 8 路径
    "17": "/home/byx/.jdks/corretto-17.0.14/bin/java"      # Java 11 路径
}

JAR_TASKS = {
    # 格式：任务名 -> (JAR路径, 配置文件名, 工作目录)
    "cha": (
        "/home/byx/projects/Tai-e/build/tai-e-all-0.5.2-SNAPSHOT.jar",
        "cha-config.yml",
        "/home/byx/projects/Tai-e" # None表示使用项目目录
    ),
    "cs1call": (
        "/home/byx/projects/Tai-e/build/tai-e-all-0.5.2-SNAPSHOT.jar",
        "cs1call-config.yml",
        "/home/byx/projects/Tai-e" # None表示使用项目目录
    ),
    "ci": (
        "/home/byx/projects/Tai-e/build/tai-e-all-0.5.2-SNAPSHOT.jar",
        "ci-config.yml",
        "/home/byx/projects/Tai-e" # None表示使用项目目录
    ),
    "ci_app": (
        "/home/byx/projects/Tai-e/build/tai-e-all-0.5.2-SNAPSHOT.jar",
        "ci_app-config.yml",
        "/home/byx/projects/Tai-e"
    )
}
# ==================================================


def load_excluded_projects(csv_path):
    """读取特殊异常项目列表"""
    excluded = []
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            # 跳过可能存在的标题行 [3](@ref)
            header = next(reader, None)  # 兼容空文件
            # 读取所有行的第一列数据 [3,5](@ref)
            excluded = [row[0] for row in reader if row]
    except FileNotFoundError:
        print(f"警告：未找到文件 {csv_path}")
    return excluded

def run_command(task_name: str, java_path: str, jar_path: str,
                config_file: str, project_dir: Path,
                work_dir: Path = None):
    """执行命令并生成任务专属日志"""
    # 创建任务专属日志目录
    task_log_dir = project_dir / f"{task_name}_logs"
    task_log_dir.mkdir(exist_ok=True)

    # 生成带时间戳的日志文件
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = task_log_dir / f"run_{timestamp}.log"

    # 确定工作目录
    final_work_dir = work_dir or project_dir
    final_work_dir = final_work_dir.resolve()

    # 构建命令
    cmd = [
        java_path,
        "-jar", jar_path,
        "--options-file", str(project_dir / config_file)
    ]

    # 执行监控
    start_time = time.time()
    peak_mem = 0
    exit_code = -1

    try:
        with open(log_file, "w") as log_handle:
            # 记录元信息
            log_handle.write(
                f"[Task Info]\n"
                f"Task Name: {task_name}\n"
                f"Java Path: {java_path}\n"
                f"JAR Path: {jar_path}\n"
                f"Config File: {config_file}\n"
                f"Project Dir: {project_dir}\n"
                f"Work Dir: {final_work_dir}\n"
                f"Log File: {log_file}\n"
                f"\n[Command]\n{' '.join(cmd)}\n\n"
                f"[Output]\n"
            )

            # 启动进程
            process = subprocess.Popen(
                cmd,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                cwd=final_work_dir,
                text=True
            )

            # 内存监控
            ps_process = psutil.Process(process.pid)
            while process.poll() is None:
                try:
                    mem = ps_process.memory_info().rss
                    peak_mem = max(peak_mem, mem)
                    time.sleep(0.1)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    break

            exit_code = process.wait()

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"\n[ERROR] {str(e)}")

    # 记录性能数据
    with open(log_file, "a") as f:
        f.write(
            f"\n[Performance]\n"
            f"Start Time: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Duration: {time.time() - start_time:.2f}s\n"
            f"Peak Memory: {peak_mem / 1024**2:.2f} MB\n"
            f"Exit Code: {exit_code}\n"
        )

    return {
        "task": task_name,
        "project": project_dir.name,
        "exit_code": exit_code,
        "duration": round(time.time() - start_time, 2),
        "log_path": str(log_file)
    }

def main():

    # 参数解析
    parser = argparse.ArgumentParser(
        description="多任务日志分离执行器",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Java版本选择
    java_group = parser.add_mutually_exclusive_group(required=True)
    java_group.add_argument("--java-version",
                            choices=JAVA_VERSIONS.keys(),
                            help="预设Java版本")
    java_group.add_argument("--java",
                            help="手动指定Java路径")

    # 任务选择
    task_group = parser.add_mutually_exclusive_group(required=True)
    task_group.add_argument("--task",
                            choices=JAR_TASKS.keys(),
                            help="预设任务名称")
    task_group.add_argument("--jar",
                            help="手动指定JAR路径（需配合--config使用）")

    # 可选参数
    parser.add_argument("--config",
                        help="配置文件名（手动模式必填）")
    parser.add_argument("--work-dir",
                        help="覆盖工作目录（优先于预设任务的配置）")
    parser.add_argument("--root", required=True,
                        help="包含子项目目录的根路径")

    args = parser.parse_args()

    # 解析Java路径
    java_path = args.java or JAVA_VERSIONS[args.java_version]
    if not Path(java_path).exists():
        raise FileNotFoundError(f"Java路径无效: {java_path}")

    # 解析任务配置
    task_name = "custom"
    if args.task:
        task_name = args.task
        task_config = JAR_TASKS[task_name]
        jar_path = task_config[0]
        config_file = task_config[1]
        default_work_dir = task_config[2] if len(task_config) > 2 else None
        final_work_dir = args.work_dir or default_work_dir
    else:
        jar_path = args.jar
        config_file = args.config
        final_work_dir = args.work_dir
        if not config_file:
            raise ValueError("手动指定JAR时需要提供--config参数")

    # 路径验证
    if not Path(jar_path).exists():
        raise FileNotFoundError(f"JAR文件不存在: {jar_path}")

    # 处理工作目录路径
    if final_work_dir:
        final_work_dir = Path(final_work_dir).resolve()
        if not final_work_dir.exists():
            raise FileNotFoundError(f"工作目录不存在: {final_work_dir}")

    # 验证根目录
    root_dir = Path(args.root)
    if not root_dir.is_dir():
        raise NotADirectoryError(f"无效的项目根目录: {root_dir}")


    # 初始化总日志路径
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    summary_path = Path(__file__).parent / ".task_summary"/ f"{task_name}"
    summary_path.mkdir(exist_ok=True)
    summary_log = summary_path / f"task_summary_{timestamp}.log"

    # 初始化结果记录
    results = []

    # 使用示例
    # excluded_list = load_excluded_projects(root_dir/".reports"/"blacklist.csv")
    excluded_list = ['.lib', '.idea', '.task_summary', '.reports', '.git']
    print(f"需排除的项目：{excluded_list}")

    # 遍历处理子目录
    for project_dir in root_dir.iterdir():

        if project_dir.name in excluded_list:
            print(f"需排除的项目：{project_dir}")
            continue
        
        if project_dir.is_dir():
            print(f"\n{' 开始处理 ':^40}")
            print(f"项目: {project_dir.name}")
            print(f"任务: {task_name}")

            # 验证配置文件
            config_path = project_dir / config_file
            if not config_path.exists():
                print(f" ! 配置文件缺失: {config_file}")
                continue

            # 执行任务
            result = run_command(
                task_name=task_name,
                java_path=java_path,
                jar_path=jar_path,
                config_file=config_file,
                project_dir=project_dir,
                work_dir=final_work_dir
            )

            # 记录结果
            results.append(result)
            print(f" √ 完成 | 耗时: {result['duration']}s | 状态码: {result['exit_code']}")
            print(f" 日志路径: {result['log_path']}")

    # 生成总日志
    with open(summary_log, "w") as f:
        f.write(f"Task Summary ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n")
        f.write("="*50 + "\n")
        f.write(f"Total Tasks: {len(results)}\n")
        f.write(f"Success Tasks: {sum(1 for r in results if r['exit_code'] == 0)}\n\n")

        f.write("Details:\n")
        f.write("-"*50 + "\n")
        for result in results:
            status = "SUCCESS" if result["exit_code"] == 0 else "FAILED"
            f.write(
                f"Project: {result['project']}\n"
                f"Task: {result['task']}\n"
                f"Duration: {result['duration']}s\n"
                f"Status: {status} (Code: {result['exit_code']})\n"
                f"Log: {result['log_path']}\n"
                f"{'-'*30}\n"
            )

    print(f"\n任务执行总结已保存至: {summary_log}")

if __name__ == "__main__":
    main()