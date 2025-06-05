import os
import argparse

from attr.filters import exclude


def delete_large_files(root_dir, max_size_mb=100, exclude_dirs=None):
    """
    删除超过指定大小的大文件，跳过黑名单文件夹
    :param root_dir: 要扫描的根目录
    :param max_size_mb: GitHub的文件大小限制(MB)
    :param exclude_dirs: 要排除的文件夹名称列表
    """
    if exclude_dirs is None:
        exclude_dirs = []
    # 标准化排除目录名称（大小写敏感）
    exclude_dirs = set(name for name in exclude_dirs)

    max_size_bytes = max_size_mb * 1024 * 1024
    deleted_count = 0
    skipped_count = 0
    failed_files = []

    print(f"扫描目录: {os.path.abspath(root_dir)}")
    print(f"文件大小限制: {max_size_mb}MB ({max_size_bytes} 字节)")
    if exclude_dirs:
        print(f"排除的文件夹: {', '.join(sorted(exclude_dirs))}")

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 跳过黑名单目录
        if any(excluded in os.path.normpath(dirpath).split(os.sep) for excluded in exclude_dirs):
            skipped_count += 1
            continue

        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                file_size = os.path.getsize(file_path)
                if file_size > max_size_bytes:
                    if any(excluded in os.path.normpath(dirpath).split(os.sep) for excluded in exclude_dirs):
                        print(f"跳过(黑名单内): {file_path} ({file_size / (1024 * 1024):.2f}MB)")
                        skipped_count += 1
                    else:
                        print(f"发现大文件: {file_path} ({file_size / (1024 * 1024):.2f}MB)")
                        os.remove(file_path)
                        print(f"已删除: {file_path}")
                        deleted_count += 1
            except Exception as e:
                failed_files.append((file_path, str(e)))

    print("\n操作完成:")
    print(f"- 已删除文件数量: {deleted_count}")
    print(f"- 跳过文件/文件夹: {skipped_count}")

    if failed_files:
        print("\n以下文件删除失败:")
        for file_path, error in failed_files:
            print(f"- {file_path}: {error}")
    elif not deleted_count and not skipped_count:
        print("- 未发现超过限制的大文件")

if __name__ == "__main__":

    if not os.path.isdir(os.getcwd()):
        print(f"错误: '{os.getcwd()}' 不是有效目录")
        exit(1)

    exclude = [".lib",".git",".idea",".reports",".task_summary",".gitignore"]

    delete_large_files(os.getcwd(), 100, exclude)