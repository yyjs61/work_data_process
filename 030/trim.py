import os
import shutil
from pathlib import Path
import logging

# 配置日志输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[logging.StreamHandler()]
)

def flatten_received_dirs(base_dir: str, dry_run: bool = False, clean_empty_parent: bool = True):
    """
    将 received 下的二级目录扁平化并重命名至 received 根目录
    例: received\A\ISO100 -> received\A_ISO100
    """
    base_path = Path(base_dir)
    if not base_path.is_dir():
        logging.error(f"❌ 目标路径不存在: {base_path}")
        return

    mode_tag = "[预演模式] " if dry_run else ""
    logging.info(f"🚀 {mode_tag}开始处理目录: {base_path}")
    
    stats = {"moved": 0, "skipped": 0, "error": 0, "cleaned": 0}
    
    # 获取所有一级目录（按名称排序保证可重复性）
    lvl1_dirs = sorted([d for d in base_path.iterdir() if d.is_dir()])

    for lvl1_dir in lvl1_dirs:
        lvl2_dirs = sorted([d for d in lvl1_dir.iterdir() if d.is_dir()])
        if not lvl2_dirs:
            continue

        for lvl2_dir in lvl2_dirs:
            new_name = f"{lvl1_dir.name}_{lvl2_dir.name}"
            target_path = base_path / new_name

            if target_path.exists():
                logging.warning(f"⚠️ 跳过: 目标已存在 {target_path}")
                stats["skipped"] += 1
                continue

            if dry_run:
                logging.info(f"🔍 {mode_tag}{lvl2_dir} -> {target_path}")
                stats["moved"] += 1
                continue

            try:
                # 同盘移动优先使用 pathlib.rename (原子操作，极快)
                # 跨盘或权限受限时 fallback 到 shutil.move
                try:
                    lvl2_dir.rename(target_path)
                except OSError:
                    shutil.move(str(lvl2_dir), str(target_path))
                logging.info(f"✅ 已移动: {lvl2_dir.name} -> {target_path.name}")
                stats["moved"] += 1
            except Exception as e:
                logging.error(f"❌ 移动失败 {lvl2_dir}: {e}")
                stats["error"] += 1

        # 可选：清空一级目录后删除空文件夹，保持 received 目录整洁
        if clean_empty_parent and not dry_run:
            try:
                if not any(lvl1_dir.iterdir()):
                    lvl1_dir.rmdir()
                    stats["cleaned"] += 1
                    logging.info(f"🧹 已清理空目录: {lvl1_dir.name}")
            except Exception as e:
                logging.warning(f"⚠️ 清理失败 {lvl1_dir.name}: {e}")

    logging.info(f"📊 处理完成 | 移动: {stats['moved']} | 跳过: {stats['skipped']} | 失败: {stats['error']} | 清理: {stats['cleaned']}")

if __name__ == "__main__":
    # 👇 修改为你的实际路径
    BASE_DIR = r"D:\Data\2026_06\01\wb_stats_0529\received"
    
    # 首次运行强烈建议开启 dry_run=True 确认无误后再执行真实移动
    flatten_received_dirs(BASE_DIR, dry_run=False, clean_empty_parent=True)