import os
import numpy as np
from pathlib import Path
import sys

# ==================== ISP 测试配置区 ====================
# BASE_DIR = Path(r"D:\Data\2026_04\29\IAC4_IMX01F_DCG_Wide_20260211")
BASE_DIR = Path(r"D:\Data\2026_06\09\V3_imx01f_20260609")
INPUT_DIR  = BASE_DIR / "unpack_raw"
OUTPUT_DIR = BASE_DIR / "unpack_raw_crop"

# RAW 基础参数（请根据 Sensor 规格确认）
# ORIG_H, ORIG_W = 4096, 3600   # 原始尺寸 (3584 + 8*2 = 3600)
# OUT_H, OUT_W   = 4096, 3584   # 目标尺寸
ORIG_H, ORIG_W = 3600, 4096   # 原始尺寸 (3584 + 8*2 = 3600)
OUT_H, OUT_W   = 3584, 4096   # 目标尺寸
# RAW_DTYPE      = np.uint16    # unpack 后通常为 16bit 对齐
RAW_DTYPE      = '<u2'    # unpack 后通常为 16bit 对齐
ENDIAN         = '<'          # '<' 小端序, '>' 大端序 (多数 MIPI RAW 为小端)
# =======================================================

def load_raw(filepath):
    """读取 RAW 文件并校验尺寸"""
    file_size = filepath.stat().st_size
    # expected_bytes = ORIG_H * ORIG_W * np.dtype(RAW_DTYPE).itemsize
    expected_bytes = ORIG_H * ORIG_W * 2
    
    if file_size != expected_bytes:
        raise RuntimeError(f"文件大小不匹配!\n  期望: {expected_bytes} bytes\n  实际: {file_size} bytes")
        
    # fromfile 比 reshape+astype 更快，适合 ISP 批量处理
    # data = np.fromfile(filepath, dtype=f"{ENDIAN}{RAW_DTYPE.__name__}")
    data = np.fromfile(filepath, dtype=RAW_DTYPE)
    return data.reshape(ORIG_H, ORIG_W)

def crop_and_save(in_path: Path, out_path: Path):
    """执行左右 Crop 并保存"""
    try:
        raw_2d = load_raw(in_path)
        # # 左右各裁 8 列
        # cropped = raw_2d[:, 8:-8]

        # 上下各裁8行
        cropped = raw_2d[8:-8, :]
        
        if cropped.shape != (OUT_H, OUT_W):
            raise ValueError(f"裁剪后尺寸异常: {cropped.shape} != ({OUT_H}, {OUT_W})")
            
        cropped.tofile(out_path)
        return True, cropped.shape
    except Exception as e:
        return False, str(e)

def main():
    print("="*60)
    print("📷 ISP RAW Crop Pipeline")
    print(f"📂 输入: {INPUT_DIR}")
    print(f"📂 输出: {OUTPUT_DIR}")
    print(f"📐 尺寸: {ORIG_H}x{ORIG_W} → {OUT_H}x{OUT_W} (左右 Crop 8)")
    print("="*60)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    scenes = sorted([d for d in INPUT_DIR.iterdir() if d.is_dir()])
    if not scenes:
        print(" 未找到任何场景文件夹，请检查路径。")
        sys.exit(1)
        
    success_cnt, fail_cnt = 0, 0
    
    for scene_dir in scenes:
        print(f"\n🔹 处理场景: {scene_dir.name}")
        out_scene_dir = OUTPUT_DIR / scene_dir.name
        out_scene_dir.mkdir(exist_ok=True)
        
        raw_files = sorted(scene_dir.glob("*.raw"))
        if not raw_files:
            print(f"   ⚠️ 未找到 .raw 文件，跳过")
            continue
            
        for raw_file in raw_files:
            out_file = out_scene_dir / raw_file.name
            ok, res = crop_and_save(raw_file, out_file)
            
            if ok:
                print(f"   ✅ {raw_file.name} -> {res}")
                success_cnt += 1
            else:
                print(f"   ❌ {raw_file.name} 失败: {res}")
                fail_cnt += 1
                break

                
    print("\n" + "="*60)
    print(f"🏁 处理完成 | 成功: {success_cnt} | 失败: {fail_cnt}")
    print("="*60)

if __name__ == "__main__":
    main()

# import matplotlib.pyplot as plt
# test = np.fromfile(r"D:\Data\2026_04\29\IAC4_IMX01F_DCG_Wide_20260211\unpack_raw\00__v078001_scene3_night_pushin/000_61487.raw", dtype='<u2').reshape(4096, 3600)
# plt.imshow(test, cmap='gray')
# plt.show()