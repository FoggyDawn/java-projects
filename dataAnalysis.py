import os
import pandas as pd
from collections import defaultdict

# 全局记录器
project_status = defaultdict(lambda: {'tasks': set(), 'errors': defaultdict(set)})
SPECIAL_EXCEPTION = "java.lang.RuntimeException: Main-class has no main method!"
SOOT_REASON = "java.lang.RuntimeException: Failed to convert"
NO_REACHABLE = "no reachable"

def parse_exception(line):
    """解析异常行并返回标准分类"""
    if line == "no reachable":
        return "no reachable"
    # 定义状态标记
    IN_THREAD = 0      # 正在解析线程名
    IN_CLASS = 1        # 正在解析异常类
    IN_REASON = 2       # 正在解析原因
    AFTER_COLON = 3     # 遇到冒号后的状态

    state = IN_THREAD
    buffer = []
    exception_class = ""
    reason = ""
    quote_count = 0     # 引号计数器（网页6的字符统计方案）

    for i, char in enumerate(line):
        # 状态机逻辑（网页5的状态转换方案）
        if state == IN_THREAD:
            if char == '"':
                quote_count += 1
                if quote_count == 2:  # 结束线程名解析
                    state = IN_CLASS
            continue

        if state == IN_CLASS:
            if char == ':':
                exception_class = ''.join(buffer).strip()
                buffer = []
                state = AFTER_COLON
            elif char == '<' :  # 类名结束条件
                exception_class = ''.join(buffer).strip()
                break
            elif i == len(line)-1 :
                buffer.append(char)
                exception_class = ''.join(buffer).strip()
                break
            else:
                buffer.append(char)

        if state == AFTER_COLON:
            if char == '<' :  # 原因结束条件
                reason = ''.join(buffer).strip()
                break
            elif i == len(line)-1 :
                buffer.append(char)
                reason = ''.join(buffer).strip()
                break
            buffer.append(char)
    print(f"{exception_class}{reason}")
    # 后处理逻辑
    if not reason and exception_class:
        return exception_class
    return f"{exception_class}{reason}" if reason else exception_class

def update_project_status(task_name, project, exceptions):
    """记录项目在各任务中的异常状态"""
    project_status[project]['tasks'].add(task_name)

    if exceptions:
        for e in set(exceptions):
            project_status[project]['errors'][task_name].add(e)
    else:
        project_status[project]['errors'][task_name].add("Success")

def analyze_tasks(task_list, root_dir="."):
    # 初始化特殊记录
    special_runtime = set()
    success_projects = set(os.listdir("."))
    bad_projects = set(os.listdir("."))  # 初始包含所有项目  # 初始包含所有项目
    exclude_dirs = ['.lib', '.idea','.task_summary','.reports','.git']
    for strs in exclude_dirs:
        success_projects.remove(strs)
        bad_projects.remove(strs)

    for task in task_list:
        csv_path = os.path.join(root_dir, f"{task}_summary.csv")

        if not os.path.exists(csv_path):
            print(f"警告：未找到任务文件 {csv_path}")
            continue

        df = pd.read_csv(csv_path)

        # 分类存储结构
        category_dict = defaultdict(list)

        for _, row in df.iterrows():
            # 解析异常分类
            if row['异常信息'] != '无':
                exceptions = [parse_exception(e) for e in row['异常信息'].split(';')]
                categories = [e for e in exceptions if e]

                # 记录特殊异常
                if SPECIAL_EXCEPTION in categories or NO_REACHABLE in categories or SOOT_REASON in categories:
                    special_runtime.add(row['项目名称'])
            else:
                categories = ["Success"]

            # 更新分类
            for cat in set(categories):
                category_dict[cat].append(row['项目名称'])

            # 更新全局状态
            update_project_status(task, row['项目名称'], categories)

        # 生成分类CSV
        output_df = pd.DataFrame([
            {'分类':k, '项目列表':','.join(v)}
            for k,v in category_dict.items()
        ])
        output_df.to_csv(os.path.join(root_dir, f"{task}_category.csv"), index=False)

        # 更新全成功项目
        success_projects &= set(df[df['运行状态']=='成功']['项目名称'])

    bad_projects ^= success_projects
    # 生成特殊报告
    pd.DataFrame({'未指定正确入口': list(special_runtime)}).to_csv(os.path.join(root_dir, "special_runtime.csv"), index=False)
    pd.DataFrame({'全成功项目': list(success_projects)}).to_csv(os.path.join(root_dir, "all_success.csv"), index=False)
    pd.DataFrame({'缺失库项目': list(bad_projects)}).to_csv(os.path.join(root_dir, "lack_deps.csv"), index=False)

if __name__ == "__main__":
    task_list = ["cha"]  # 用户提供的任务列表
    analyze_tasks(task_list, root_dir=".reports")