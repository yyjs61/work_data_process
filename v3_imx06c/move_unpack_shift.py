#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本名称: unpack_and_shift_raw.py
功能说明: 将received下的场景RAW文件进行解包，然后移位保持低位有效
工作流程:
1. 遍历received下的所有场景文件夹
2. 对每个场景的RAW文件进行解包（使用libSequentialUnpacker.dll）
3. 解包后的文件保存到unpack_raw下的对应场景目录
4. 对解包后的文件进行移位操作，保持低位有效
"""

import ctypes
import glob
import os
import numpy as np
import natsort

# ===================== 配置部分 =====================
# ROOT = r'D:\Data\2026_05\20\V3_imx06c_20260520'
# ROOT = r"D:\Data\2026_05\22\硬仿过blc模块raw"
ROOT = r"D:\Data\2026_06\04\V3_imx06c_20260604"

RECEIVED = os.path.join(ROOT, 'received')
UNPACK_RAW = os.path.join(ROOT, 'unpack_raw')

# 解包参数（根据实际Sensor规格调整）
# HEIGHT = 4096
HEIGHT = 3072
WIDTH = 4096
STRIDE = 5120
# STRIDE = 7168
IN_PACK_BIT_DEPTH = 10
OUT_UNPACK_BIT_DEPTH = 10
# IN_PACK_BIT_DEPTH = 14
# OUT_UNPACK_BIT_DEPTH = 14

# 移位检测参数
SHIFT_CANDIDATES = [6, 4, 2]
ZERO_RATIO_THRESH = 0.99999

# ===================== 解包函数 =====================

def rawPreprocess(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth, in_filepath, out_filepath):
    """调用DLL进行RAW文件解包"""
    try:
        # 尝试加载Windows DLL
        lib = ctypes.windll.LoadLibrary('./v3_imx06c/libSequentialUnpacker.dll')
    except:
        try:
            # 尝试加载Linux SO
            lib = ctypes.cdll.LoadLibrary('./v3_imx06c/libSequentialUnpacker.so')
        except:
            print(f"❌ 错误: 无法加载解包库文件")
            return False
    
    in_filepath_c_str = ctypes.c_char_p(bytes(in_filepath, 'utf-8'))
    out_filepath_c_str = ctypes.c_char_p(bytes(out_filepath, 'utf-8'))
    
    try:
        lib.sequentialUnpacker(height, width, stride, in_pack_bit_depth, 
                             out_unpack_bit_depth, in_filepath_c_str, out_filepath_c_str)
        return True
    except Exception as e:
        print(f"❌ 解包失败: {e}")
        return False

# ===================== 移位函数 =====================

def detect_shift_bits(arr, zero_ratio_thresh=ZERO_RATIO_THRESH):
    """
    检测需要右移的位数
    
    参数:
        arr: numpy数组
        zero_ratio_thresh: 低位为零的比例阈值
    
    返回:
        int: 需要右移的位数，如果不需要移位则返回0
    """
    for shift in SHIFT_CANDIDATES:
        mask = (1 << shift) - 1
        zeros = np.count_nonzero((arr & mask) == 0)
        ratio = zeros / arr.size
        if ratio > zero_ratio_thresh:
            return shift
    return 0

def shift_raw_file(file_path):
    """
    对RAW文件进行移位操作
    
    参数:
        file_path: RAW文件路径
    
    返回:
        int: 实际移位的位数
    """
    data = np.fromfile(file_path, dtype=np.uint16)
    shift_bits = detect_shift_bits(data)
    
    if shift_bits > 0:
        print(f"  [SHIFT] 右移 {shift_bits} 位")
        data = data >> shift_bits
        data.tofile(file_path)
        return shift_bits
    else:
        print(f"  [KEEP] 无需移位")
        return 0

# ===================== 主处理函数 =====================

def process_scene(scene_name):
    """
    处理单个场景
    
    参数:
        scene_name: 场景名称
    """
    print(f"\n{'='*70}")
    print(f"处理场景: {scene_name}")
    print(f"{'='*70}")
    
    # 源目录和目标目录
    src_scene_dir = os.path.join(RECEIVED, scene_name)
    dst_scene_dir = os.path.join(UNPACK_RAW, scene_name)
    
    # 检查源目录
    if not os.path.isdir(src_scene_dir):
        print(f"⚠️  跳过: {scene_name} (不是目录)")
        return
    
    # 创建目标目录
    os.makedirs(dst_scene_dir, exist_ok=True)
    
    # 检查是否已处理
    if len(os.listdir(dst_scene_dir)) > 0:
        print(f"⚠️  跳过: {scene_name} (目标目录非空，可能已处理)")
        return
    
    # 获取所有RAW文件
    raw_files = natsort.natsorted(glob.glob(os.path.join(src_scene_dir, '*.raw')))
    
    if not raw_files:
        print(f"⚠️  跳过: {scene_name} (未找到RAW文件)")
        return
    
    print(f"找到 {len(raw_files)} 个RAW文件")
    
    # 处理每个RAW文件
    for i, src_file in enumerate(raw_files):
        filename = os.path.basename(src_file)
        dst_file = os.path.join(dst_scene_dir, filename)
        
        print(f"\n[{i+1}/{len(raw_files)}] 处理: {filename}")
        
        # 步骤1: 解包
        print(f"  解包中...")
        if not rawPreprocess(HEIGHT, WIDTH, STRIDE, IN_PACK_BIT_DEPTH, 
                           OUT_UNPACK_BIT_DEPTH, src_file, dst_file):
            print(f"  ❌ 解包失败，跳过此文件")
            continue
        
        # 步骤2: 移位
        print(f"  移位处理...")
        shift_bits = shift_raw_file(dst_file)
        
        # 显示文件信息
        file_size = os.path.getsize(dst_file)
        print(f"  ✓ 完成 - 文件大小: {file_size:,} 字节")
    
    print(f"\n✅ 场景 {scene_name} 处理完成")

def main():
    """主函数"""
    print("="*70)
    print(" RAW文件解包与移位处理工具 ")
    print("="*70)
    print(f"ROOT目录: {ROOT}")
    print(f"输入目录: {RECEIVED}")
    print(f"输出目录: {UNPACK_RAW}")
    print(f"解包参数: {HEIGHT}x{WIDTH}, stride={STRIDE}")
    print(f"位深: {IN_PACK_BIT_DEPTH}bit -> {OUT_UNPACK_BIT_DEPTH}bit")
    print(f"移位检测: {SHIFT_CANDIDATES}")
    print("="*70)
    
    # 检查输入目录
    if not os.path.exists(RECEIVED):
        print(f"❌ 错误: 找不到received目录: {RECEIVED}")
        return
    
    # 检查解包库
    if not os.path.exists('./v3_imx06c/libSequentialUnpacker.dll') and \
       not os.path.exists('./v3_imx06c/libSequentialUnpacker.so'):
        print(f"❌ 错误: 找不到解包库文件 (libSequentialUnpacker.dll/.so)")
        print(f"   请确保库文件与脚本在同一目录")
        return
    
    # 创建输出根目录
    os.makedirs(UNPACK_RAW, exist_ok=True)
    
    # 获取所有场景
    scenes = natsort.natsorted([s for s in os.listdir(RECEIVED) 
                                if os.path.isdir(os.path.join(RECEIVED, s)) 
                                and not s.startswith('.')])
    
    if not scenes:
        print(f"❌ 错误: received目录下未找到场景文件夹")
        return
    
    print(f"\n找到 {len(scenes)} 个场景需要处理")
    
    # 处理每个场景
    success_count = 0
    for scene in scenes:
        try:
            process_scene(scene)
            success_count += 1
        except Exception as e:
            print(f"\n❌ 处理场景 {scene} 时出错: {e}")
            import traceback
            traceback.print_exc()
    
    # 总结
    print("\n" + "="*70)
    print(f"处理完成！")
    print(f"成功处理: {success_count}/{len(scenes)} 个场景")
    print(f"输出目录: {UNPACK_RAW}")
    print("="*70)

if __name__ == '__main__':
    main()