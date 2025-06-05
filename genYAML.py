import os
import glob
import shutil
from pathlib import Path

from Crypto.SelfTest.Cipher.test_OFB import file_name
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)  # 控制缩进格式
yaml.preserve_quotes = True  # 保留引号
# 基础配置模板路径
# BASE_CONFIG_PATH = "/home/byx/testSpace/javaprjs/options.yml"  # 用户需要提前准备好的基础配置文件

def phase1(projects_root, lib_dir, option_file_name):
    """
    第一阶段：生成项目配置（绝对路径模式）
    :param option_file_name: 生成的文档名称
    :param projects_root: 项目根目录（绝对路径，如 /home/user/projects）
    :param lib_dir: 公共库目录（绝对路径，如 /home/user/default-lib）
    """


    # 获取所有公共库的绝对路径
    lib_dir = Path(lib_dir).resolve()
    print(lib_dir)
    jar_paths = [
        str(jar.resolve())  # 强制转换为绝对路径
        for jar in lib_dir.glob("**/*.jar")
        if jar.is_file()
    ]

    exclude_dirs = ['.lib', '.idea','.task_summary','.reports']

    # 为每个项目生成配置
    for project_dir in Path(projects_root).iterdir():
        dir_name = project_dir.name
        if project_dir.is_dir() and (dir_name not in exclude_dirs):
            config = CommentedMap()

            # 读取基础配置模板
            with open(project_dir/"taie-config.yml") as f:
                base_config = yaml.load(f)

            if "classPath" in base_config:
                base_config.move_to_end("classPath")

            # 先复制基础配置（保留顺序）
            for key in base_config:
                if key != "classPath":
                    config[key] = base_config[key]

            # 最后添加 classPath 和项目特定字段
            config["classPath"] = jar_paths  # 确保 classPath 在最后
            config["appClassPath"] = [str(project_dir / "bin")]

            # 写入项目目录
            config_path = project_dir / option_file_name  # "taie-config.yml"
            with open(config_path, "w") as f:
                yaml.dump(config, f)

def phase2(config_path, jre_base=Path("/home/byx/projects/Tai-e/java-benchmarks/JREs")):
    """
    第二阶段：补充 JRE 依赖
    """
    with open(config_path) as f:
        config = yaml.load(f)

    # 验证 javaVersion
    # if config.get("javaVersion") is None:
    #     return
    java_version = int(config.get("javaVersion"))
    print("java_version is ", java_version)
    try:
        if not (3 <= java_version <= 8):
            raise ValueError(f"Invalid javaVersion: {java_version} in {config_path}")
    except ValueError:
        return

    # 添加 JRE jars
    jre_dir = jre_base / f"jre1.{java_version}"
    new_jars = [
        str(jar.resolve())  # 绝对路径
        for jar in jre_dir.rglob("*.jar")
        if jar.is_file()
    ]

    # 去重添加（保持 classPath 在最后）
    existing = set(config.get("classPath", []))
    config["classPath"] += [jar for jar in new_jars if jar not in existing]

    # 确保 classPath 保持在最后
    if "classPath" in config:
        config.move_to_end("classPath")

    # 写回文件
    with open(config_path, "w") as f:
        yaml.dump(config, f)

def change_config_all(projects_root, config_name, output_dir, exclude_dirs=None):
    """
    处理项目目录，排除特定文件夹
    :param projects_root: 项目根目录路径
    :param exclude_dirs: 要排除的目录名列表（默认包含 ['.lib', '.idea']）
    """
    exclude_dirs = exclude_dirs or ['.lib', '.idea','.task_summary','.reports']
    projects_root = Path(projects_root).resolve()

    # 遍历所有子目录
    for project_dir in projects_root.iterdir():
        # 跳过非目录项
        if not project_dir.is_dir():
            continue

        # 获取目录名并检查是否在排除列表
        dir_name = project_dir.name
        if dir_name in exclude_dirs:
            print(f"跳过排除目录: {dir_name}")
            continue

        # 正式处理项目目录
        print(f"处理项目: {dir_name}")
        # ... 此处调用你的业务逻辑 ...


        config_path = project_dir / config_name
        with open(config_path) as f:
            config = yaml.load(f)

        # 改变输出路径（已完成）
        output_dir_path = project_dir / output_dir#"cs1call-output" #"taie-output"
        output_dir_path.mkdir(parents=True, exist_ok=True)
        #
        config["outputDir"] = str((project_dir / output_dir).resolve())

        config["allowPhantom"] = False

        # 改变pta算法
        config["analyses"] = {'cg': 'algorithm:cha;dump:true;dump-methods:true;dump-call-edges:true;'}
        # config["analyses"]["pta"] = "cs:ci;implicit-entries:false;handle-invokedynamic:true"

        # 改变cache模式
        config["worldCacheMode"] = False

        # 改变运行Scope
        config["scope"] = "APP"

        # 写回文件
        with open(config_path, "w") as f:
            yaml.dump(config, f)


# 使用示例
if __name__ == "__main__":
    # 第一阶段：生成项目配置
    # phase1(
    #     projects_root="/home/byx/testSpace/javaprjs",  # 包含多个项目的根目录
    #     lib_dir="./.lib",       # 公共库目录
    #     option_file_name="cha-config.yml"
    # )
    #
    # # 第二阶段：补充 JRE 路径
    # for config_file in Path("/home/byx/testSpace/javaprjs").rglob("cha-config.yml"):
    #     print(config_file)
    #     phase2(config_file)

    # 第三阶段：修改全部config
    change_config_all(projects_root="/home/byx/testSpace/javaprjs",config_name="cha-config.yml",output_dir="cha-output")