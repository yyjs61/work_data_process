#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
20bit RAW Unpack Tool (基于SequentialUnpacker逻辑)
功能：将 MIPI packed RAW20 解包为 uint32 (低位对齐)
直接运行此脚本即可自动处理指定目录下的所有 .raw 文件
"""

import os
import re
import gc
import time
import numpy as np
from pathlib import Path

# ==================== 配置区域 ====================
# 输入目录：存放原始 packed raw 文件
ROOT = r"D:\Data\2026_05\09\yifeng"
# 输出目录：存放解包后的 unpack raw 文件
OUTPUT_DIR = r"D:\Data\2026_05\09\unpack_raw"
# =================================================

def parse_resolution(filename: str):
    """从文件名中解析宽高，支持 w[4096]_h[3584] 格式"""
    match = re.search(r'w\[(\d+)\]_h\[(\d+)\]', filename)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

def unpack_raw20_to_uint32(packed_data: bytes, width: int, height: int) -> np.ndarray:
    """
    基于SequentialUnpacker逻辑的 20bit -> 32bit 解包
    
    逻辑还原：
    1. 将 10 字节视为一个流。
    2. 提取 4 个像素 (P0, P1, P2, P3)，每个 20 bit。
    3. 将 20 bit 值放入 uint32 的低位。
    """
    total_pixels = width * height
    
    # 20bit packed 每 4 像素占 10 字节
    # 如果文件大小不匹配，可能是包含了 padding，这里取有效数据部分
    expected_bytes = total_pixels * 10 // 4
    if len(packed_data) > expected_bytes:
        print(f"   ⚠️  检测到文件包含多余数据 (可能是 stride padding)，仅处理有效像素数据。")
        packed_data = packed_data[:expected_bytes]
    
    # 1. 转换为 numpy 数组并重塑为 (组数, 10)
    # 注意：必须保证数据长度是 10 的倍数
    num_groups = len(packed_data) // 10
    packed_array = np.frombuffer(packed_data, dtype=np.uint8)[:num_groups * 10].reshape((num_groups, 10))
    
    # 2. 按列提取字节 (模拟 C++ 中的 binary_value 拼接)
    b0 = packed_array[:, 0]
    b1 = packed_array[:, 1]
    b2 = packed_array[:, 2]
    b3 = packed_array[:, 3]
    b4 = packed_array[:, 4]
    b5 = packed_array[:, 5]
    b6 = packed_array[:, 6]
    b7 = packed_array[:, 7]
    b8 = packed_array[:, 8]
    b9 = packed_array[:, 9]
    
    # 转换为 uint32 以进行位运算
    b0 = b0.astype(np.uint32)
    b1 = b1.astype(np.uint32)
    b2 = b2.astype(np.uint32)
    b3 = b3.astype(np.uint32)
    b4 = b4.astype(np.uint32)
    b5 = b5.astype(np.uint32)
    b6 = b6.astype(np.uint32)
    b7 = b7.astype(np.uint32)
    b8 = b8.astype(np.uint32)
    b9 = b9.astype(np.uint32)
    
    # 3. 位移与掩码提取 (还原 SequentialUnpacker 逻辑)
    # P0: Byte 0, 1, Byte 2 的低 4 位 (Bits 0-19)
    p0 = b0 | (b1 << 8) | ((b2 & 0x0F) << 16)
    
    # P1: Byte 2 的高 4 位, Byte 3, 4 (Bits 20-39)
    p1 = ((b2 & 0xF0) >> 4) | (b3 << 4) | (b4 << 12)
    
    # P2: Byte 5, 6, Byte 7 的低 4 位 (Bits 40-59)
    p2 = b5 | (b6 << 8) | ((b7 & 0x0F) << 16)
    
    # P3: Byte 7 的高 4 位, Byte 8, 9 (Bits 60-79)
    p3 = ((b7 & 0xF0) >> 4) | (b8 << 4) | (b9 << 12)
    
    # 4. 掩码处理 (确保只有低 20 位有效)
    mask = 0xFFFFF
    p0 &= mask
    p1 &= mask
    p2 &= mask
    p3 &= mask
    
    # 5. 合并结果 (Interleave: P0, P1, P2, P3, P0, P1...)
    # 创建一个空数组
    output_flat = np.empty(total_pixels, dtype=np.uint32)
    
    # 填充 (注意：如果最后有余数，确保不越界)
    count = min(num_groups * 4, total_pixels)
    
    output_flat[0::4][:num_groups] = p0
    output_flat[1::4][:num_groups] = p1
    output_flat[2::4][:num_groups] = p2
    output_flat[3::4][:num_groups] = p3
    
    # 截断可能存在的填充（如果 total_pixels 不是 4 的倍数）
    final_data = output_flat[:total_pixels].reshape((height, width))
    
    return final_data

def process_raw_file(raw_file: Path, out_path: Path):
    """处理单个RAW文件"""
    print(f"\n正在处理: {raw_file.name}")
    
    try:
        # 1. 解析分辨率
        w, h = parse_resolution(raw_file.name)
        if w is None or h is None:
            raise ValueError("文件名未包含 w[x]_h[y] 分辨率标识")
        
        # 2. 读取 packed 数据
        with open(raw_file, "rb") as f:
            packed_data = f.read()
        
        # 3. 执行解包
        print("   ⚙️ 正在解包 (20bit -> uint32 低位对齐)...")
        unpacked_array = unpack_raw20_to_uint32(packed_data, w, h)
        
        # 4. 保存结果（.raw后缀）
        out_filename = f"{raw_file.stem}_unpack.raw"
        out_file = out_path / out_filename
        unpacked_array.tofile(out_file)
        
        # 打印统计信息
        print(f"   ✅ 分辨率: {w} x {h}")
        print(f"    输入大小: {len(packed_data)/1024/1024:.2f} MB")
        print(f"   📤 输出大小: {out_file.stat().st_size/1024/1024:.2f} MB")
        print(f"   📊 数据范围: [{unpacked_array.min()}, {unpacked_array.max()}]")
        print(f"   💾 数据类型: {unpacked_array.dtype}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 处理失败: {e}")
        return False

def main():
    root_path = Path(ROOT)
    out_path = Path(OUTPUT_DIR)
    
    if not root_path.exists():
        print(f"❌ 错误：输入目录不存在 -> {root_path}")
        return
        
    # 创建输出目录
    out_path.mkdir(parents=True, exist_ok=True)
    
    # 获取所有 raw 文件
    raw_files = sorted(list(root_path.glob("*.raw")) + list(root_path.glob("*.Raw")))
    if not raw_files:
        print(f"⚠️  提示：在 {root_path} 中未找到 .raw 文件")
        return
        
    print(f"📂 输入目录 : {root_path}")
    print(f" 输出目录 : {out_path}")
    print(f"📋 待处理文件数: {len(raw_files)}")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    t_start = time.time()
    
    for idx, raw_file in enumerate(raw_files, 1):
        print(f"\n[{idx}/{len(raw_files)}]")
        if process_raw_file(raw_file, out_path):
            success_count += 1
        else:
            fail_count += 1
        
        # 释放内存
        gc.collect()
        
    t_end = time.time()
    print("\n" + "=" * 60)
    print(f"🏁 批量处理完成!")
    print(f"   ✅ 成功: {success_count} 个  |  ❌ 失败: {fail_count} 个")
    print(f"   ⏱️  总耗时: {t_end - t_start:.2f} 秒")
    print("=" * 60)

if __name__ == "__main__":
    main()