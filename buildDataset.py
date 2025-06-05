import os
import shutil

# 定义基准目录列表（根据实际路径调整）
base_dirs = [
    "../xcorpus/data/qualitas_corpus_20130901",
    "../xcorpus/data/xcorpus-extension-20170313"
]

# 获取当前工作目录
output_dir = os.getcwd()

for base_dir in base_dirs:
    # 遍历基准目录下的所有项目目录
    for prj_name in os.listdir(base_dir):
        prj_dir = os.path.join(base_dir, prj_name)

        # 检查是否是有效目录
        if os.path.isdir(prj_dir):
            src_project = os.path.join(prj_dir, "project")
            dst_project = os.path.join(output_dir, prj_name)

            # 如果源project目录存在
            if os.path.exists(src_project):
                try:
                    # 复制并覆盖已存在的目录
                    shutil.copytree(src_project, dst_project, dirs_exist_ok=True)
                    print(f"成功复制：{prj_name}")
                except Exception as e:
                    print(f"复制失败[{prj_name}]：{str(e)}")
            else:
                print(f"项目缺失project目录：{prj_name}")