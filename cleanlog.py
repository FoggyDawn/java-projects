import argparse
from pathlib import Path

def clean_root_logs(root_dir: Path, patterns: list, dry_run: bool):
    """清理项目根目录下的散乱日志"""
    deleted_files = []

    # 遍历每个项目目录
    for project_dir in root_dir.iterdir():
        if project_dir.is_dir():
            print(f"\n检查项目: {project_dir.name}")

            # 在项目根目录（不包含子目录）查找日志文件
            for pattern in patterns:
                for log_file in project_dir.glob(pattern):
                    if log_file.is_file() and log_file.parent == project_dir:
                        print(f"发现散乱日志: {log_file.name}")
                        deleted_files.append(log_file)

    if not deleted_files:
        print("\n未找到需要清理的散乱日志")
        return

    # 预演模式只显示不删除
    if dry_run:
        print("\n预演模式：以下文件将被删除")
        for f in deleted_files:
            print(f"  {f}")
        return

    # 确认执行
    confirm = input(f"\n确认删除 {len(deleted_files)} 个散乱日志文件？(y/N) ").lower()
    if confirm != 'y':
        print("操作已取消")
        return

    # 执行删除
    success_count = 0
    for f in deleted_files:
        try:
            f.unlink()
            success_count += 1
            print(f"已删除: {f}")
        except Exception as e:
            print(f"删除失败 [{f}]: {str(e)}")

    print(f"\n清理完成！成功删除 {success_count} 个文件")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="项目根目录散乱日志清理工具")
    parser.add_argument("root_dir",
                        help="包含多个项目目录的根路径（例如：./projects）")
    parser.add_argument("-p", "--patterns",
                        nargs='+', default=["*.log"],
                        help="要清理的日志文件模式（默认：*.log）")
    parser.add_argument("--dry-run",
                        action="store_true",
                        help="预演模式（仅显示不删除）")

    args = parser.parse_args()

    clean_root_logs(
        root_dir=Path(args.root_dir),
        patterns=args.patterns,
        dry_run=args.dry_run
    )