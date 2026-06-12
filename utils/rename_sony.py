import os
import glob
import re
from pathlib import Path
import logging

# 配置日志输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[logging.StreamHandler()]
)

# ================= 配置区 =================
# BASE_DIR = r"D:\Data\2026_06\01\IMX06C_binning_normal_4k_20260514\output_beforeDRC_bayer"
BASE_DIR = r"D:\Data\2026_06\10\output_beforeDRC_bayer"
# BASE_DIR = r"D:\Data\2026_06\01\IMX06C_binning_normal_4k_20260514\test"
# 目标文件名格式：帧序号_场景名_自定义后缀.dat
# 例如：000_scene00_800_noFace_raw_uint32_imx06c_binning.dat
TARGET_SUFFIX = "rawpp_0610_uint32_imx06c_binning"
# ⚠️ 首次运行务必保持 True，仅打印映射关系不修改文件
# DRY_RUN = True
DRY_RUN = False
# ==========================================

def extract_scene_name(filename):
    """
    从文件名中提取场景名
    例如：000_scene00_800_noFace_PreFusion_off_MFNR_on__uint32...
    提取：scene00_800_noFace
    """
    # 匹配模式：数字_场景名_后续参数
    # 场景名格式：sceneXX_数字_face/noFace
    match = re.search(r'\d+_(scene\d+_\d+_(?:face|noFace))_', filename)
    if match:
        return match.group(1)
    else:
        # 如果没有匹配到标准格式，尝试提取第一个下划线后的部分
        parts = filename.split('_')
        if len(parts) >= 3:
            # 假设场景名是第2-4个部分（去掉帧序号）
            return '_'.join(parts[1:4])
        return None

def rename_scene_dat_files(base_dir: str, dry_run: bool = True):
    base_path = Path(base_dir)
    if not base_path.is_dir():
        logging.error(f"❌ 目标路径不存在: {base_path}")
        return

    mode_tag = "[预演模式] " if dry_run else ""
    logging.info(f"🚀 {mode_tag}开始扫描目录: {base_path}")
    stats = {"renamed": 0, "skipped": 0, "error": 0}

    # 遍历所有场景子文件夹（按名称排序保证可重复性）
    for scene_dir in sorted(base_path.iterdir()):
        if not scene_dir.is_dir():
            continue

        # 获取该场景下所有 .dat 文件
        dat_files = sorted(scene_dir.glob("*.dat"))
        if not dat_files:
            continue

        logging.info(f"📂 {mode_tag}处理场景文件夹: {scene_dir.name} (共 {len(dat_files)} 个文件)")

        for old_path in dat_files:
            old_name = old_path.name
            
            # 提取开头的帧序号 (例如 000, 001, 012)
            frame_match = re.match(r'^(\d+)_', old_name)
            frame_prefix = frame_match.group(1) if frame_match else "000"
            
            # 提取场景名 (例如 scene00_800_noFace)
            scene_name = extract_scene_name(old_name)
            if scene_name:
                logging.debug(f"  提取场景名: {scene_name}")
            else:
                scene_name = f"scene_unknown_{frame_prefix}"
                logging.warning(f"  ⚠️ 未提取到场景名，使用默认: {scene_name}")

            # 生成新文件名：帧序号_场景名_后缀.dat
            new_name = f"{frame_prefix}_{scene_name}_{TARGET_SUFFIX}.dat"
            new_path = old_path.parent / new_name

            # 跳过无效操作
            if old_path == new_path:
                stats["skipped"] += 1
                continue
            if new_path.exists():
                logging.warning(f"⚠️ 跳过: 目标文件已存在 {new_path}")
                stats["skipped"] += 1
                continue

            if dry_run:
                logging.info(f" {mode_tag}{old_name}")
                logging.info(f"    -> {new_name}")
                stats["renamed"] += 1
            else:
                try:
                    # pathlib.rename 在同盘符下为原子操作，速度极快
                    old_path.rename(new_path)
                    logging.info(f"✅ {old_name}")
                    logging.info(f"    -> {new_name}")
                    stats["renamed"] += 1
                except Exception as e:
                    logging.error(f"❌ 重命名失败 {old_name}: {e}")
                    stats["error"] += 1

    logging.info(f"📊 处理完成 | 重命名: {stats['renamed']} | 跳过: {stats['skipped']} | 失败: {stats['error']}")

if __name__ == "__main__":
    rename_scene_dat_files(BASE_DIR, dry_run=DRY_RUN)