import os
import zipfile

def extract_zips_in_projects():
    # 获取当前工作目录
    base_dir = os.getcwd()

    # 遍历当前目录下的所有项目目录
    for project_name in os.listdir(base_dir):
        project_path = os.path.join(base_dir, project_name)

        if os.path.isdir(project_path):
            # 遍历项目目录中的文件
            for item in os.listdir(project_path):
                if item.endswith('.zip'):
                    zip_path = os.path.join(project_path, item)
                    # 创建解压目录（去除.zip后缀）
                    extract_dir = os.path.splitext(zip_path)[0]
                    os.makedirs(extract_dir, exist_ok=True)

                    try:
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            zip_ref.extractall(extract_dir)
                        print(f"✅ 解压成功：{project_name}/{item}")
                    except zipfile.BadZipFile:
                        print(f"❌ 损坏的ZIP文件：{project_name}/{item}")
                    except Exception as e:
                        print(f"⚠️ 解压失败[{project_name}/{item}]：{str(e)}")

if __name__ == "__main__":
    extract_zips_in_projects()