#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本名称: shift_raw_bitdepth.py
功能说明: 将 unpack_raw 下每个场景的 RAW 文件从高位对齐的 10bit 右移为低位对齐的 10bit
"""

import os
import glob
import natsort
import numpy as np

# ===================== 配置部分 =====================
ROOT = r'D:\Data\2026_05\19\IMX06C_binning_normal_4k_20260514'
UNPACK_RAW = os.path.join(ROOT, 'unpack_raw')

# 图像参数
IMAGE_WIDTH = 4096
IMAGE_HEIGHT = 3072
SHIFT_BITS = 6  # 右移位数（16bit存储，10bit有效，高位对齐→低位对齐）

# ===================== 主程序 =====================

def process_scene(scene_path, scene_name):
    """
    处理单个场景下的所有 RAW 文件
    
    参数:
        scene_path: 场景文件夹路径
        scene_name: 场景名称
    """
    print(f"\n处理场景: {scene_name}")
    
    # 获取所有 RAW 文件
    raw_files = glob.glob(os.path.join(scene_path, '*.raw'))
    raw_files = [f for f in raw_files if not os.path.basename(f).startswith('.')]
    raw_files = natsort.natsorted(raw_files)
    
    if not raw_files:
        print(f"  ⚠️  未找到 RAW 文件")
        return
    
    print(f"  找到 {len(raw_files)} 个 RAW 文件")
    print(f"  执行右移 {SHIFT_BITS} 位操作")
    
    # 处理每个文件
    for i, raw_file in enumerate(raw_files):
        filename = os.path.basename(raw_file)
        file_size = os.path.getsize(raw_file)
        
        try:
            # 读取 RAW 数据
            raw_data = np.fromfile(raw_file, dtype=np.uint16)
            
            # 验证文件大小
            expected_size = IMAGE_WIDTH * IMAGE_HEIGHT
            if len(raw_data) != expected_size:
                print(f"  ⚠️  警告: {filename} 大小不匹配 (期望 {expected_size}, 实际 {len(raw_data)})")
            
            # 右移操作：高位对齐 → 低位对齐
            shifted_data = raw_data >> SHIFT_BITS
            
            # 写回文件（覆盖原文件）
            shifted_data.tofile(raw_file)
            
            # 进度显示
            if (i + 1) % 10 == 0 or (i + 1) == len(raw_files):
                print(f"    已处理: {i + 1}/{len(raw_files)}")
        
        except Exception as e:
            print(f"  ❌ 处理失败 {filename}: {e}")
    
    print(f"  ✅ 完成: {scene_name}")


def main():
    """主函数"""
    print("=" * 70)
    print(" RAW 文件位深移位工具 ")
    print("=" * 70)
    print(f"ROOT目录: {ROOT}")
    print(f"输入目录: {UNPACK_RAW}")
    print(f"操作: 右移 {SHIFT_BITS} 位 (高位对齐10bit → 低位对齐10bit)")
    print("=" * 70)
    
    # 检查目录
    if not os.path.exists(UNPACK_RAW):
        print(f"❌ 错误: 找不到 unpack_raw 目录: {UNPACK_RAW}")
        return
    
    # 获取所有场景
    scenes = [s for s in os.listdir(UNPACK_RAW) 
              if os.path.isdir(os.path.join(UNPACK_RAW, s)) and not s.startswith('.')]
    scenes = natsort.natsorted(scenes)
    
    if not scenes:
        print("❌ 错误: 未找到任何场景文件夹")
        return
    
    print(f"\n找到 {len(scenes)} 个场景需要处理\n")
    
    # 处理每个场景
    for scene_name in scenes:
        scene_path = os.path.join(UNPACK_RAW, scene_name)
        try:
            process_scene(scene_path, scene_name)
        except Exception as e:
            print(f"❌ 处理场景 {scene_name} 时出错: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print(" 所有场景处理完成！")
    print("=" * 70)


if __name__ == '__main__':
    main()