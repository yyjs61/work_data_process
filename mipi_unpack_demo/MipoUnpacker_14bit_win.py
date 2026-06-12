#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIPI RAW Batch Unpacker (DLL 调用版)
目录结构:
  ROOT/
    ├── received/
    │   ├── scene_A/
    │   │   ├── frame01.raw
    │   │   ── frame02.raw
    │   └── scene_B/
    │       ── ...
    └── unpack_raw/
        ├── scene_A/
        │   ├── frame01.raw
        │   └── frame02.raw
        └── scene_B/
            └── ...
"""

import ctypes
import glob
import os
import sys

# ==================== 🛠️ 核心配置区 ====================
# Windows DLL 路径 (若为 Linux 请改为 .so 路径)
DLL_PATH = r"./_lib/libMipiUnpacker.dll"

# 根目录 (请根据实际情况修改)
ROOT = r"D:\Data\2026_06\09\V3_imx01f_EVT2p3_sensor_raw_20260609"
INPUT_ROOT  = os.path.join(ROOT, "received")
OUTPUT_ROOT = os.path.join(ROOT, "unpack_raw")

# ISP 解包参数 (需与 Sensor 实际输出一致)
HEIGHT = 3584                  # 图像高度
WIDTH  = 4096                  # 图像宽度
STRIDE = 7168                 # 行步长 (字节) = WIDTH * IN_PACK_BIT_DEPTH / 8
IN_PACK_BIT_DEPTH = 14         # 输入压缩位深 (10/12/14/20)
OUT_UNPACK_BIT_DEPTH = 14      # 输出目标位深 (建议 32 以匹配 uint32 低位对齐)
# ======================================================


def setup_dll():
    """加载 DLL 并绑定 C 接口签名"""
    if not os.path.exists(DLL_PATH):
        raise FileNotFoundError(f" 未找到 DLL 文件: {DLL_PATH}\n   请确保 DLL 与脚本同级，或修改 DLL_PATH")
        
    lib = ctypes.CDLL(DLL_PATH)
    
    # 严格匹配接口: extern "C" int mipiUnpacker(int, int, int, int, int, char*, char*)
    lib.mipiUnpacker.argtypes = [
        ctypes.c_int,      # height
        ctypes.c_int,      # width
        ctypes.c_int,      # stride
        ctypes.c_int,      # in_pack_bit_depth
        ctypes.c_int,      # out_unpack_bit_depth
        ctypes.c_char_p,   # in_filepath
        ctypes.c_char_p    # out_filepath
    ]
    lib.mipiUnpacker.restype = ctypes.c_int
    return lib

def process_scene(lib, scene_name, scene_in_dir, scene_out_dir):
    """处理单个场景下的所有 RAW 文件"""
    os.makedirs(scene_out_dir, exist_ok=True)
    
    # 兼容多种后缀
    patterns = ["*.raw", "*.RAW"]
    raw_files = []
    for p in patterns:
        raw_files.extend(glob.glob(os.path.join(scene_in_dir, p)))
    raw_files = sorted(list(set(raw_files)))
    
    if not raw_files:
        print(f"  ⚠️ 跳过: {scene_name} (无 RAW 文件)")
        return
        
    print(f"📂 场景: {scene_name} | 共 {len(raw_files)} 个文件")
    for idx, file in enumerate(raw_files, 1):
        filename = os.path.basename(file)
        out_name = filename  # 保持原名，也可改为 f"unpacked__{filename}"
        out_path = os.path.join(scene_out_dir, out_name)
        
        # 路径转 C 兼容 bytes
        in_c  = ctypes.c_char_p(file.encode('utf-8'))
        out_c = ctypes.c_char_p(out_path.encode('utf-8'))
        
        # 调用 DLL
        ret = lib.mipiUnpacker(
            HEIGHT, WIDTH, STRIDE,
            IN_PACK_BIT_DEPTH, OUT_UNPACK_BIT_DEPTH,
            in_c, out_c
        )
        
        if ret == 0:
            print(f"  ✅ [{idx}/{len(raw_files)}] {filename}")
        else:
            print(f"   [{idx}/{len(raw_files)}] {filename} ❌ 失败(码:{ret})")

def main():
    # 1. 验证输入目录
    if not os.path.exists(INPUT_ROOT):
        print(f"❌ 输入目录不存在: {INPUT_ROOT}")
        sys.exit(1)
        
    # 2. 加载 DLL
    lib = setup_dll()
    
    # 3. 获取所有场景文件夹
    scenes = sorted([
        d for d in os.listdir(INPUT_ROOT) 
        if os.path.isdir(os.path.join(INPUT_ROOT, d))
    ])
    
    print("=" * 60)
    print(f"📂 ROOT      : {ROOT}")
    print(f"📥 INPUT_DIR : {INPUT_ROOT}")
    print(f"📤 OUTPUT_DIR: {OUTPUT_ROOT}")
    print(f"⚙️  参数配置 : {WIDTH}x{HEIGHT} | Stride={STRIDE} | {IN_PACK_BIT_DEPTH}bit → {OUT_UNPACK_BIT_DEPTH}bit")
    print(f"📦 发现场景数 : {len(scenes)}")
    print("=" * 60)
    
    # 4. 逐场景处理
    for scene in scenes:
        scene_in  = os.path.join(INPUT_ROOT, scene)
        scene_out = os.path.join(OUTPUT_ROOT, scene)
        process_scene(lib, scene, scene_in, scene_out)
        
    print("=" * 60)
    print("🏁 批量解包完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()