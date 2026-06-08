#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAW to JPG Visualization Tool
功能：读取 unpack 后的 20bit RAW (uint32 低位对齐)，应用 ISP Gain，可视化保存为 JPG
直接运行即可批量处理，无需参数
"""

import re
import gc
import time
import numpy as np
import cv2
from pathlib import Path

# ==================== 配置区域 ====================
# 输入目录：存放 unpack 后的 .raw 文件 (uint32, 20bit 低位对齐)
ROOT = r"D:\Data\2026_05\09\unpack_raw"
# 输出目录：存放可视化 JPG
OUTPUT_DIR = r"D:\Data\2026_05\09\visualized_jpg"
# ISP Gain 参数 (线性乘数)
ISP_GAIN = 24.0
# =================================================

def parse_resolution(filename: str):
    """从文件名解析宽高 (支持 w[4096]_h[3584] 格式)"""
    match = re.search(r'w\[(\d+)\]_h\[(\d+)\]', filename)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

def visualize_raw_to_jpg(raw_file: Path, out_dir: Path, gain: float):
    """单文件处理核心逻辑"""
    print(f"\n处理: {raw_file.name}")
    try:
        # 1. 解析分辨率
        w, h = parse_resolution(raw_file.name)
        if w is None or h is None:
            raise ValueError("无法解析分辨率 (文件名需包含 w[x]_h[y])")

        # 2. 读取 RAW 数据 (uint32)
        raw_data = np.fromfile(raw_file, dtype=np.uint32)
        expected_pixels = w * h
        
        # 兼容可能存在的文件头/尾部填充
        if raw_data.size < expected_pixels:
            raise ValueError(f"文件数据不足: 期望 {expected_pixels}, 实际 {raw_data.size}")
        img_raw = raw_data[:expected_pixels].reshape((h, w))

        # 3. 应用 ISP Gain
        # 使用 float32 计算防止中间结果溢出，同时节省内存
        img_gain = img_raw.astype(np.float32) * gain

        # 4. 硬件限幅 (Clip to 20bit Max)
        # ISP  pipeline 中 Gain 后通常会 saturate 到 sensor 位深上限
        max_20bit = (1 << 20) - 1  # 1048575
        img_clipped = np.clip(img_gain, 0, max_20bit).astype(np.uint32)

        # 5. 转换为 8bit 用于 JPG 显示
        # 方案A (推荐 ISP 调试): 直接右移 12 位 (取高 8 位)，保持线性关系
        img_8bit = (img_clipped >> 12).astype(np.uint8)
        
        # 方案B (如需拉伸对比度): 线性归一化到 0-255
        # img_8bit = ((img_clipped / max_20bit) * 255).astype(np.uint8)

        # 6. 保存 JPG (单通道灰度图)
        out_path = out_dir / f"{raw_file.stem}.jpg"
        cv2.imwrite(str(out_path), img_8bit, [cv2.IMWRITE_JPEG_QUALITY, 95])

        # 打印调试信息
        print(f"   ✅ 完成 | 原始范围: [{img_raw.min()}, {img_raw.max()}]")
        print(f"   ⚡ Gain后范围: [{img_clipped.min()}, {img_clipped.max()}] (限幅至 {max_20bit})")
        return True

    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return False

def main():
    root_path = Path(ROOT)
    out_path = Path(OUTPUT_DIR)
    out_path.mkdir(parents=True, exist_ok=True)

    # 查找所有 unpack 后的 raw 文件
    raw_files = sorted(list(root_path.glob("*.raw")))
    if not raw_files:
        print(f"⚠️ 未在 {root_path} 中找到 .raw 文件，请确认 unpack 步骤已完成")
        return

    print(f"📂 输入目录 : {root_path}")
    print(f"️  输出目录 : {out_path}")
    print(f"⚙️  ISP Gain : {ISP_GAIN}")
    print("=" * 60)

    t_start = time.time()
    success_cnt, fail_cnt = 0, 0

    for idx, raw_file in enumerate(raw_files, 1):
        print(f"[{idx}/{len(raw_files)}]", end=" ")
        if visualize_raw_to_jpg(raw_file, out_path, ISP_GAIN):
            success_cnt += 1
        else:
            fail_cnt += 1
        gc.collect()  # 及时释放内存

    t_end = time.time()
    print("\n" + "=" * 60)
    print(f"🏁 批量可视化完成!")
    print(f"   ✅ 成功: {success_cnt} 个  |  ❌ 失败: {fail_cnt} 个")
    print(f"   ⏱️  总耗时: {t_end - t_start:.2f} 秒")
    print("=" * 60)

if __name__ == "__main__":
    main()