import os
import glob
import shutil

def make_lib():
    # 获取当前工作目录
    base_dir = os.getcwd()

    lib = "/home/byx/testSpace/javaprjs/.lib"
    # 遍历当前目录下的所有项目目录
    for project_name in os.listdir(base_dir):
        project_path = os.path.join(base_dir, project_name)

        if os.path.isdir(project_path):
            # 遍历项目目录中的文件
            lib_dir = os.path.join(project_path, 'default-lib')
            for jarpath in glob.glob(os.path.join(lib_dir, '*.jar')):
                if os.path.isfile(jarpath):
                    shutil.copy2(
                        jarpath,
                        lib
                    )
                else:
                    print(f"Warning: JDK jar not found: {jarpath}")

if __name__ == '__main__':
    make_lib()