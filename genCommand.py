


# 已弃用



# import os
# import glob
# import shutil
#
# def generate_commands(projects_root):
#     # 固定参数配置
#     a_params = [
#         '-a "pta=cs:2-type;"',
#         '-a "cg=algorithm:pta;dump:true;dump-methods:true;dump-call-edges:true;"'
#     ]
#
#     for project_dir in os.listdir(projects_root):
#         project_path = os.path.join(projects_root, project_dir)
#         bin_path = os.path.join(project_path, 'bin')
#
#         # 过滤非项目目录
#         if not os.path.isdir(project_path) or not os.path.exists(bin_path):
#             continue
#
#         # 构建命令参数
#         command = []
#
#         # 添加-acp参数
#         command.append(f'-acp "{os.path.normpath(bin_path)}"')
#
#         # 添加所有jar依赖（包括刚复制的）
#         lib_dir = os.path.join(project_path, 'default-lib')
#         for jar in glob.glob(os.path.join(lib_dir, '*.jar')):
#             command.append(f'-cp "{os.path.normpath(jar)}"')
#
#         # 添加固定分析参数
#         command.extend(a_params)
#
#         # 添加执行参数（保持示例中的顺序）
#         command.append('-m artofillusion.ArtOfIllusion')
#         command.append('-java _')
#
#         # 写入命令文件
#         output_path = os.path.join(project_path, 'command.txt')
#         with open(output_path, 'w', encoding='utf-8') as f:
#             f.write(' '.join(command))
#         print(f'Generated: {output_path}')
#
# if __name__ == '__main__':
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     generate_commands(script_dir)