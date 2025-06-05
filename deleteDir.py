import os
import csv
import argparse
import shutil
from pathlib import Path

def delete_directories_from_csv(csv_path):
    # 获取当前工作目录
    current_dir = Path.cwd()
    print(f"当前工作目录: {current_dir}")

    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                # 取每行第一个元素作为目录名（可调整索引）
                dir_name = row[0].strip()
                target_dir = current_dir / dir_name
                print(target_dir)

                if not target_dir.exists():
                    print(f"[跳过] 目录不存在: {target_dir}")
                    continue

                if not target_dir.is_dir():
                    print(f"[错误] {target_dir} 是文件而非目录")
                    continue

                try:
                    # 删除非空目录需改用 shutil.rmtree(target_dir)
                    # os.rmdir(target_dir)
                    shutil.rmtree(target_dir)
                    print(f"[成功] 已删除目录: {target_dir}")
                except OSError as e:
                    print(f"[失败] 删除 {target_dir} 失败: {e.strerror}")

    except FileNotFoundError:
        print(f"[错误] CSV文件不存在: {csv_path}")
    except Exception as e:
        print(f"[异常] 发生未预期错误: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='根据CSV文件删除目录')
    parser.add_argument('csv_path', help='CSV文件路径（包含目录名列表）')
    args = parser.parse_args()

    delete_directories_from_csv(args.csv_path)