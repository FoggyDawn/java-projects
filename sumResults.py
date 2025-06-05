import os
import re
from datetime import datetime
import csv

def parse_log_time(filename):
    """解析文件名中的时间戳"""
    match = re.search(r"run_(\d{8})-(\d{6})\.log", filename)
    if match:
        return datetime.strptime(f"{match.group(1)}{match.group(2)}", "%Y%m%d%H%M%S")
    return None

def analyze_log(log_path):
    """分析日志文件内容"""
    exceptions = []
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("Exception "):
                exceptions.append(line.strip())
            elif line.startswith("Call graph has 0 reachable "):
                exceptions.append("no reachable")
    return {
        'status': '失败' if exceptions else '成功',
        'exceptions': exceptions
    }

def summarize_results(root_dir, task_name, output_file):
    """主处理函数"""
    results = []
    exclude_dirs = ['.lib', '.idea','.task_summary','.reports']

    for project in os.listdir(root_dir):

        if project in exclude_dirs:
            print(f"跳过排除项目: {project}")
            continue
        project_path = os.path.join(root_dir, project)
        task_logs_dir = os.path.join(project_path, f"{task_name}_logs")  # 动态路径生成

        # 验证路径有效性
        if not os.path.exists(task_logs_dir) or not os.path.isdir(task_logs_dir):
            continue

        # 筛选相关日志文件
        log_files = []
        for filename in os.listdir(task_logs_dir):
            if filename.startswith(f"run_") and filename.endswith(".log"):
                log_time = parse_log_time(filename)
                if log_time:
                    log_files.append((log_time, filename))

        if not log_files:
            continue

        # 选择最新日志
        latest_log = max(log_files, key=lambda x: x[0])
        log_path = os.path.join(task_logs_dir, latest_log[1])

        # 分析日志内容
        analysis = analyze_log(log_path)
        results.append({
            '项目名称': project,
            '日志文件': latest_log[1],
            '检测时间': latest_log[0].strftime("%Y-%m-%d %H:%M:%S"),
            '运行状态': analysis['status'],
            '异常信息': '; '.join(analysis['exceptions']) if analysis['exceptions'] else '无'
        })

    # 保存结果
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['项目名称', '日志文件', '检测时间', '运行状态', '异常信息'])
        writer.writeheader()
        writer.writerows(results)

    print(f"分析完成！结果已保存至：{output_file}")

# 使用示例
if __name__ == "__main__":
    summarize_results(
        root_dir="/home/byx/testSpace/javaprjs",  # 替换为实际根目录路径
        task_name="cha",
        output_file=".reports/cha_summary.csv"
    )