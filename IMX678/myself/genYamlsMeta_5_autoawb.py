#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本名称: genYamlsMeta_2.py
功能说明: 为多个场景数据生成每一帧对应的YAML配置文件，并自动计算AWB增益
          (支持标准RGGB Bayer格式)

目录结构:
ROOT/
├─ unpack_raw/
│  ├─ 场景1_unpack/
│  │  ├─ frame1.raw
│  │  └─ ...
│  └─ 场景2_unpack/
├─ yamls_eachFrame/
│  ├─ 场景1_unpack/
│  │  ├─ 000.yaml (包含 awb_gain_r, awb_gain_b)
│  │  └─ ...
│  └─ 场景2_unpack/
├─ 场景1_unpack.yaml
└─ ...
"""

import os
import yaml
import glob
import numpy as np

# ===================== 配置部分 =====================
ROOT = r'D:\Data\2026_05\18\Test_data_260515'
RAW_BASE_DIR = 'unpack_raw'
OUTPUT_BASE_DIR = 'yamls_eachFrame3'

# ===================== AWB算法配置 =====================
AWB_CONFIG = {
    'enable': True,                    # 是否启用AWB计算
    'method': 'white_patch',     # 算法选择（见上表）
    'params': {
        'low_thresh': 0.15,            # 灰度世界：排除<15%亮度的像素
        'high_thresh': 0.85,           # 灰度世界：排除>85%亮度的像素
        'percentile': 99,              # 白色补丁：取99%分位
    }
}

# 传感器参数配置（根据实际Sensor规格修改）
SENSOR_PARAMS = {
    'height': 2160,          # Quad Bayer原始高度
    'width': 3840,           # Quad Bayer原始宽度
    'black_level': 64,       # 黑电平
    'white_level': 4095,     # 白电平 (12bit: 4095, 10bit: 1023)
    'bayer_pattern': 'RGGB',  # Bayer排列: RGGB, GBRG, GRBG, BGGR
    'bit_depth': 12          # 位深 (10, 12, 14等)
}

# 是否启用AWB计算
ENABLE_AWB_CALCULATION = True

# ===================== AWB计算函数 =====================

def read_raw_file(file_path, height, width, bit_depth=12):
    """
    读取标准Bayer格式的Raw文件
    
    参数:
        file_path: Raw文件路径
        height: 图像高度
        width: 图像宽度
        bit_depth: 位深 (10/12/14 bit)
    
    返回:
        numpy.ndarray: Bayer图像数据
    """
    try:
        # 根据位深选择数据类型
        if bit_depth <= 8:
            dtype = np.uint8
        elif bit_depth <= 16:
            dtype = np.uint16
        else:
            raise ValueError(f"不支持的位深: {bit_depth}")
        
        # 读取Raw数据
        raw_data = np.fromfile(file_path, dtype=dtype).reshape([height, width]).astype(np.float32)
        
        return raw_data
    except Exception as e:
        print(f"    ⚠️ 读取Raw文件失败: {e}")
        return None


# def calculate_awb_gain(img_data, black_level, white_level, bayer_pattern):
    """
    基于灰度世界算法计算 AWB 增益
    
    参数:
        img_data: Bayer图像数据 (标准Bayer格式)
        black_level: 黑电平
        white_level: 白电平
        bayer_pattern: Bayer排列模式
    
    返回:
        tuple: (gain_r, gain_b)
    """
    img = img_data.astype(float)
    
    # 归一化到 [0, 1]
    range_val = white_level - black_level
    if range_val <= 0:
        return 1.0, 1.0
        
    img = (img - black_level) / range_val
    img = img.clip(0, 1)
    
    eps = 1e-6  # 防止除零
    
    # 根据Bayer排列提取R/G/B通道
    # 标准Bayer模式的2x2重复单元
    if bayer_pattern == 'RGGB':
        # R G
        # G B
        sum_r = np.sum(img[0::2, 0::2])  # R在偶数行偶数列
        sum_b = np.sum(img[1::2, 1::2])  # B在奇数行奇数列
        sum_g = np.sum(img[0::2, 1::2]) + np.sum(img[1::2, 0::2])  # G在偶数行奇数列 + 奇数行偶数列
    elif bayer_pattern == 'GBRG':
        # G B
        # R G
        sum_r = np.sum(img[1::2, 0::2])
        sum_b = np.sum(img[0::2, 1::2])
        sum_g = np.sum(img[0::2, 0::2]) + np.sum(img[1::2, 1::2])
    elif bayer_pattern == 'GRBG':
        # G R
        # B G
        sum_r = np.sum(img[0::2, 1::2])
        sum_b = np.sum(img[1::2, 0::2])
        sum_g = np.sum(img[0::2, 0::2]) + np.sum(img[1::2, 1::2])
    elif bayer_pattern == 'BGGR':
        # B G
        # G R
        sum_r = np.sum(img[1::2, 1::2])
        sum_b = np.sum(img[0::2, 0::2])
        sum_g = np.sum(img[0::2, 1::2]) + np.sum(img[1::2, 0::2])
    else:
        print(f"    ⚠️ 未知的Bayer模式: {bayer_pattern}, 使用默认增益")
        return 1.0, 1.0

    # 计算增益 (以G通道为基准)
    g_mean = sum_g / 2.0
    scale_r = max(1.0, g_mean / (sum_r + eps)) if sum_r > 0 else 1.0
    scale_b = max(1.0, g_mean / (sum_b + eps)) if sum_b > 0 else 1.0
    
    return round(scale_r, 4), round(scale_b, 4)


def calculate_scene_awb(raw_folder, height, width, black_level, white_level, bayer_pattern, bit_depth):
    """
    计算场景下所有Raw文件的AWB增益
    
    参数:
        raw_folder: Raw文件所在文件夹路径
        height, width: 传感器分辨率
        black_level, white_level: 黑/白电平
        bayer_pattern: Bayer排列
        bit_depth: 位深
    
    返回:
        list: [(gain_r, gain_b), ...] 对应每个Raw文件
    """
    raw_files = sorted([f for f in os.listdir(raw_folder) 
                        if f.endswith('.raw') and os.path.isfile(os.path.join(raw_folder, f))])
    
    awb_gains = []
    
    for idx, raw_file in enumerate(raw_files):
        file_path = os.path.join(raw_folder, raw_file)
        
        # 读取Raw文件
        bayer_img = read_raw_file(file_path, height, width, bit_depth)
        if bayer_img is None:
            awb_gains.append((1.0, 1.0))  # 失败时使用默认值
            continue
        
        # 计算AWB
        # gain_r, gain_b = calculate_awb_gain(bayer_img, black_level, white_level, bayer_pattern)
        # 计算AWB
        gain_r, gain_b = calculate_awb_gain(
            bayer_img, 
            black_level, white_level, bayer_pattern,
            method=AWB_CONFIG['method'],
            **AWB_CONFIG['params']
        )
        awb_gains.append((gain_r, gain_b))
        
        # 进度提示（每10帧打印一次）
        if (idx + 1) % 10 == 0 or (idx + 1) == len(raw_files):
            print(f"    📊 AWB计算进度: {idx + 1}/{len(raw_files)} (最新增益: R={gain_r:.3f}, B={gain_b:.3f})")
    
    return awb_gains

# ===================== AWB计算函数 (已修复尺寸不匹配问题) =====================

def calculate_awb_gain(img_data, black_level, white_level, bayer_pattern, 
                       method='gray_world_thresh', **kwargs):
    """
    多算法可选的AWB增益计算 (已修复Bayer通道尺寸不一致导致的IndexError)
    """
    img = img_data.astype(float)
    range_val = white_level - black_level
    if range_val <= 0:
        return 1.0, 1.0
    
    # 归一化 + 去黑电平
    img_norm = (img - black_level) / range_val
    img_norm = np.clip(img_norm, 0, 1)
    eps = 1e-6
    
    if method == 'gray_world':
        return _gray_world_basic(img_norm, bayer_pattern, eps)
    
    elif method == 'gray_world_thresh':
        low_thresh = kwargs.get('low_thresh', 0.15)
        high_thresh = kwargs.get('high_thresh', 0.85)
        return _gray_world_thresh_2d(img_norm, bayer_pattern, low_thresh, high_thresh, eps)
    
    elif method == 'white_patch':
        percentile = kwargs.get('percentile', 99)
        return _white_patch_2d(img_norm, bayer_pattern, percentile, eps)
    
    elif method == 'histogram':
        return _histogram_based_2d(img_norm, bayer_pattern, eps)
    
    else:
        print(f"⚠️ 未知AWB算法: {method}, 使用默认阈值灰度世界")
        return _gray_world_thresh_2d(img_norm, bayer_pattern, 0.15, 0.85, eps)


def _get_bayer_slices(bayer_pattern):
    """返回标准Bayer模式的切片索引，避免重复代码"""
    if bayer_pattern == 'RGGB':
        return (slice(0,None,2), slice(0,None,2)), \
               (slice(0,None,2), slice(1,None,2)), \
               (slice(1,None,2), slice(0,None,2)), \
               (slice(1,None,2), slice(1,None,2))
    elif bayer_pattern == 'GRBG':
        return (slice(0,None,2), slice(1,None,2)), \
               (slice(0,None,2), slice(0,None,2)), \
               (slice(1,None,2), slice(1,None,2)), \
               (slice(1,None,2), slice(0,None,2))
    elif bayer_pattern == 'GBRG':
        return (slice(1,None,2), slice(0,None,2)), \
               (slice(0,None,2), slice(0,None,2)), \
               (slice(1,None,2), slice(1,None,2)), \
               (slice(0,None,2), slice(1,None,2))
    elif bayer_pattern == 'BGGR':
        return (slice(1,None,2), slice(1,None,2)), \
               (slice(0,None,2), slice(1,None,2)), \
               (slice(1,None,2), slice(0,None,2)), \
               (slice(0,None,2), slice(0,None,2))
    else:
        raise ValueError(f"Unsupported Bayer pattern: {bayer_pattern}")


def _compute_gain(r_vals, g_vals, b_vals, eps):
    """统一计算增益的底层函数"""
    if len(r_vals) < 50 or len(b_vals) < 50:
        return 1.0, 1.0  # 有效像素不足时返回默认值
    
    g_mean = np.mean(g_vals)
    r_mean = np.mean(r_vals)
    b_mean = np.mean(b_vals)
    
    scale_r = max(1.0, g_mean / (r_mean + eps))
    scale_b = max(1.0, g_mean / (b_mean + eps))
    return round(scale_r, 4), round(scale_b, 4)


def _gray_world_basic(img, pattern, eps):
    """标准灰度世界（全图像素平均）"""
    r_s, g1_s, g2_s, b_s = _get_bayer_slices(pattern)
    r_vals = img[r_s].flatten()
    g_vals = np.concatenate([img[g1_s].flatten(), img[g2_s].flatten()])
    b_vals = img[b_s].flatten()
    return _compute_gain(r_vals, g_vals, b_vals, eps)


def _gray_world_thresh_2d(img, pattern, low_t, high_t, eps):
    """带阈值过滤的灰度世界 (2D掩码安全版)"""
    # 在完整2D图像上生成有效性掩码
    valid_mask = (img >= low_t) & (img <= high_t)
    
    r_s, g1_s, g2_s, b_s = _get_bayer_slices(pattern)
    
    # 分别应用掩码提取有效像素 (确保掩码与目标切片尺寸完全一致)
    r_vals = img[r_s][valid_mask[r_s]]
    g_vals = np.concatenate([
        img[g1_s][valid_mask[g1_s]],
        img[g2_s][valid_mask[g2_s]]
    ])
    b_vals = img[b_s][valid_mask[b_s]]
    
    # 如果过滤后像素太少，降级使用全图平均
    if len(r_vals) < 100 or len(b_vals) < 100:
        return _gray_world_basic(img, pattern, eps)
        
    return _compute_gain(r_vals, g_vals, b_vals, eps)


def _white_patch_2d(img, pattern, percentile, eps):
    """白色补丁法 (取高百分位)"""
    r_s, g1_s, g2_s, b_s = _get_bayer_slices(pattern)
    
    # 扁平化各通道
    r_flat = img[r_s].flatten()
    g_flat = np.concatenate([img[g1_s].flatten(), img[g2_s].flatten()])
    b_flat = img[b_s].flatten()
    
    r_val = np.percentile(r_flat, percentile)
    g_val = np.percentile(g_flat, percentile)
    b_val = np.percentile(b_flat, percentile)
    
    if g_val < 0.05:  # 整体过暗则降级
        return _gray_world_basic(img, pattern, eps)
        
    scale_r = max(1.0, g_val / (r_val + eps))
    scale_b = max(1.0, g_val / (b_val + eps))
    return round(scale_r, 4), round(scale_b, 4)


def _histogram_based_2d(img, pattern, eps):
    """直方图统计法 (裁剪两端极端值后求均值)"""
    def trim_mean(arr, ratio=0.05):
        if len(arr) < 200: return np.mean(arr)
        s = np.sort(arr)
        k = int(len(s) * ratio)
        return np.mean(s[k:-k])
        
    r_s, g1_s, g2_s, b_s = _get_bayer_slices(pattern)
    
    r_vals = img[r_s].flatten()
    g_vals = np.concatenate([img[g1_s].flatten(), img[g2_s].flatten()])
    b_vals = img[b_s].flatten()
    
    r_mean = trim_mean(r_vals)
    g_mean = trim_mean(g_vals)
    b_mean = trim_mean(b_vals)
    
    scale_r = max(1.0, g_mean / (r_mean + eps))
    scale_b = max(1.0, g_mean / (b_mean + eps))
    return round(scale_r, 4), round(scale_b, 4)

# ===================== 主程序 =====================

def process_scenes(root_path):
    """处理ROOT目录下的所有场景"""
    if not os.path.isdir(root_path):
        print(f"❌ 错误: ROOT目录不存在: {root_path}")
        return

    yamls_base_path = os.path.join(root_path, OUTPUT_BASE_DIR)
    os.makedirs(yamls_base_path, exist_ok=True)
    
    raws_base_path = os.path.join(root_path, RAW_BASE_DIR)
    if not os.path.isdir(raws_base_path):
        print(f"⚠️ 警告: 未找到 {RAW_BASE_DIR} 目录")
        return

    yaml_files = sorted(glob.glob(os.path.join(root_path, '*.yaml')))
    if not yaml_files:
        print(f"⚠️ 警告: ROOT目录下未找到任何 .yaml 配置文件")
        return

    print(f"📂 开始处理ROOT目录: {root_path}")
    print(f"📦 找到 {len(yaml_files)} 个场景配置文件\n")

    for yaml_path in yaml_files:
        yaml_basename = os.path.basename(yaml_path)
        scene_name = os.path.splitext(yaml_basename)[0]

        scene_raw_path = os.path.join(raws_base_path, scene_name)
        scene_output_path = os.path.join(yamls_base_path, scene_name)

        if not os.path.isdir(scene_raw_path):
            print(f"️ 跳过: {scene_name} (缺少 {RAW_BASE_DIR}/{scene_name} 文件夹)")
            continue

        raw_files = [f for f in os.listdir(scene_raw_path) 
                     if f.endswith('.raw') and os.path.isfile(os.path.join(scene_raw_path, f))]
        raws_len = len(raw_files)

        if raws_len == 0:
            print(f"⏭️ 跳过: {scene_name} (unpack_raw文件夹为空)")
            continue

        # 读取基础YAML配置
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                scene_config = yaml.safe_load(f)
            if scene_config is None:
                scene_config = {}
        except Exception as e:
            print(f"❌ 读取失败: {scene_name} ({e})")
            continue

        # 计算AWB增益（如果需要）
        awb_gains = []
        if ENABLE_AWB_CALCULATION:
            print(f"\n🔍 计算 {scene_name} 的AWB增益...")
            awb_gains = calculate_scene_awb(
                scene_raw_path,
                SENSOR_PARAMS['height'],
                SENSOR_PARAMS['width'],
                SENSOR_PARAMS['black_level'],
                SENSOR_PARAMS['white_level'],
                SENSOR_PARAMS['bayer_pattern'],
                SENSOR_PARAMS['bit_depth']
            )
            print(f"✅ AWB计算完成，共 {len(awb_gains)} 帧\n")

        # 创建输出目录
        os.makedirs(scene_output_path, exist_ok=True)

        # 生成每帧YAML
        success_count = 0
        for frame_index in range(raws_len):
            out_yaml_name = f"{str(frame_index).zfill(3)}.yaml"
            out_yaml_path = os.path.join(scene_output_path, out_yaml_name)
            
            # 复制基础配置
            frame_config = scene_config.copy() if scene_config else {}
            
            # 注入AWB增益
            if ENABLE_AWB_CALCULATION and frame_index < len(awb_gains):
                gain_r, gain_b = awb_gains[frame_index]
                
                # 确保 white_balance 节点存在
                if 'white_balance' not in frame_config:
                    frame_config['white_balance'] = {}
                
                frame_config['white_balance']['awb_gain_r'] = gain_r
                frame_config['white_balance']['awb_gain_b'] = gain_b
                frame_config['white_balance']['awb_gain_g'] = 1.0  # G通道基准

            try:
                with open(out_yaml_path, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(frame_config, f, allow_unicode=True, sort_keys=False)
                success_count += 1
            except Exception as e:
                print(f"❌ 写入失败: {scene_name}/帧{frame_index} ({e})")
                break

        print(f"✅ 完成: {scene_name}")
        print(f"    帧数: {raws_len} | 📝 成功生成: {success_count}")
        print(f"    输出至: {scene_output_path}\n")


if __name__ == '__main__':
    print("=" * 70)
    print(" ISP YAML生成器 (带AWB自动计算) ")
    print("=" * 70)
    print(f"传感器配置:")
    print(f"  - 分辨率: {SENSOR_PARAMS['width']} x {SENSOR_PARAMS['height']}")
    print(f"  - 位深: {SENSOR_PARAMS['bit_depth']} bit")
    print(f"  - 黑/白电平: {SENSOR_PARAMS['black_level']} / {SENSOR_PARAMS['white_level']}")
    print(f"  - Bayer模式: {SENSOR_PARAMS['bayer_pattern']}")
    print(f"  - AWB计算: {'启用' if ENABLE_AWB_CALCULATION else '禁用'}")
    print("=" * 70 + "\n")
    
    process_scenes(ROOT)
    
    print("=" * 70)
    print(" 所有场景YAML生成完毕！")
    print("=" * 70)