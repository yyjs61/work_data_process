#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本名称: generate_yaml_from_meta.py
功能说明: 读取received目录下的txt元数据文件，为unpack_raw中每个RAW文件生成对应的YAML配置
"""

import os
import re
import yaml
import natsort
import glob

# ===================== 配置部分 =====================
ROOT = r'D:\Data\2026_05\19\IMX06C_binning_normal_4k_20260514'
RECEIVED = os.path.join(ROOT, 'received')
UNPACK_RAW = os.path.join(ROOT, 'unpack_raw')
YAML_OUTPUT = os.path.join(ROOT, 'yamls_eachFrame')

# 图像参数
IMAGE_WIDTH = 4096
IMAGE_HEIGHT = 3072
BIT_DEPTH = 10
BLACK_LEVEL = 64
WHITE_LEVEL = 1023  # 10bit有效数据
BAYER_PATTERN = 'RGGB'

# ===================== 元数据解析函数 =====================

def parse_meta_txt(txt_path):
    """
    解析txt元数据文件，提取每一帧的AE、AWB信息
    
    参数:
        txt_path: txt文件路径
    
    返回:
        dict: {frame_index: {expotime, iso, SensorAGain, ...}}
    """
    frames_meta = {}
    
    if not os.path.exists(txt_path):
        print(f"  ⚠️  警告: 未找到元数据文件 {txt_path}")
        return frames_meta
    
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    current_frame = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 解析 AEINFO
        if line.startswith('AEINFO'):
            # 提取帧号
            frame_match = re.search(r'F\[(\d+)\]', line)
            if frame_match:
                frame_idx = int(frame_match.group(1))
                current_frame['frame_index'] = frame_idx
            
            # 提取曝光时间 S[0.980] (ms -> ns)
            s_match = re.search(r'S\[([\d.]+)\]', line)
            if s_match:
                expotime_ms = float(s_match.group(1))
                current_frame['expotime'] = int(expotime_ms * 1000000)  # ms to ns
            
            # 提取 ISO I[816]
            i_match = re.search(r'I\[(\d+)\]', line)
            if i_match:
                current_frame['iso'] = int(i_match.group(1))
            
            # 提取模拟增益 AG[8.163]
            ag_match = re.search(r'AG\[([\d.]+)\]', line)
            if ag_match:
                current_frame['SensorAGain'] = float(ag_match.group(1))
            
            # 提取数字增益 DG[1.000]
            dg_match = re.search(r'DG\[([\d.]+)\]', line)
            if dg_match:
                current_frame['SensorDGain'] = float(dg_match.group(1))
            
            # 计算 sensor gain
            if 'SensorAGain' in current_frame and 'SensorDGain' in current_frame:
                current_frame['sensorgain'] = current_frame['SensorAGain'] * current_frame['SensorDGain']
                current_frame['gain'] = current_frame['sensorgain']
            
            # 提取照度 LUX[193.022] (可选)
            lux_match = re.search(r'LUX\[([\d.]+)\]', line)
            if lux_match:
                # current_frame['lux_value'] = float(lux_match.group(1))
                current_frame['luxid'] = float(lux_match.group(1))
                current_frame['lux_index'] = float(lux_match.group(1))
        
        # 解析 AWBINFO
        elif line.startswith('AWBINFO'):
            # 提取色温 CT[4263]
            ct_match = re.search(r'CT\[(\d+)\]', line)
            if ct_match:
                ct_value = int(ct_match.group(1))
                current_frame['cct'] = ct_value

            
            # 提取 R增益 RG[9091] -> 9091/4096
            rg_match = re.search(r'RG\[(\d+)\]', line)
            if rg_match:
                rg_value = int(rg_match.group(1))
                current_frame['r_gain'] = round(rg_value / 4096.0, 6)
            
            # 提取 B增益 BG[8393] -> 8393/4096
            bg_match = re.search(r'BG\[(\d+)\]', line)
            if bg_match:
                bg_value = int(bg_match.group(1))
                current_frame['b_gain'] = round(bg_value / 4096.0, 6)
            
            # 保存当前帧数据
            if 'frame_index' in current_frame:
                frames_meta[current_frame['frame_index']] = current_frame.copy()
                current_frame = {}
    
    return frames_meta


def get_scene_mapping():
    """
    建立received场景名与unpack_raw场景名的映射关系
    
    返回:
        dict: {received_scene_name: unpack_raw_scene_name}
    """
    mapping = {}
    
    # 获取received下的所有场景（文件夹）
    received_scenes = [s for s in os.listdir(RECEIVED) 
                       if os.path.isdir(os.path.join(RECEIVED, s)) and not s.startswith('.')]
    
    # 获取unpack_raw下的所有场景
    unpack_scenes = [s for s in os.listdir(UNPACK_RAW) 
                     if os.path.isdir(os.path.join(UNPACK_RAW, s)) and not s.startswith('.')]
    
    # 建立映射：去掉unpack_raw场景的"XX__"前缀
    for unpack_scene in unpack_scenes:
        # 提取场景名（去掉"XX__"前缀）
        match = re.match(r'^\d+_(.+)$', unpack_scene)
        if match:
            base_name = match.group(1)
            if base_name in received_scenes:
                mapping[base_name] = unpack_scene
    
    return mapping


def generate_yaml_for_scene(received_scene, unpack_scene):
    """
    为单个场景生成所有帧的YAML文件
    
    参数:
        received_scene: received目录下的场景名
        unpack_scene: unpack_raw目录下的场景名（带序号前缀）
    """
    print(f"\n处理场景: {received_scene} -> {unpack_scene}")
    
    # 构造路径
    meta_txt_path = os.path.join(RECEIVED, received_scene, f"{received_scene}.txt")
    raw_dir = os.path.join(UNPACK_RAW, unpack_scene)
    yaml_output_dir = os.path.join(YAML_OUTPUT, unpack_scene)
    
    # 解析元数据
    frames_meta = parse_meta_txt(meta_txt_path)
    print(f"  解析到 {len(frames_meta)} 帧元数据")
    
    # 检查RAW目录
    if not os.path.exists(raw_dir):
        print(f"  ⚠️  警告: 未找到RAW目录 {raw_dir}")
        return
    
    # 获取RAW文件列表（去掉"XXX__"前缀后排序）
    raw_files = glob.glob(os.path.join(raw_dir, '*.raw'))
    raw_files = [f for f in raw_files if not os.path.basename(f).startswith('.')]
    
    # 按文件名排序（考虑"XXX__"前缀）
    def get_frame_index(filepath):
        basename = os.path.basename(filepath)
        match = re.match(r'^(\d+)__', basename)
        if match:
            return int(match.group(1))
        return 0
    
    raw_files.sort(key=get_frame_index)
    print(f"  找到 {len(raw_files)} 个RAW文件")
    
    # 创建YAML输出目录
    os.makedirs(yaml_output_dir, exist_ok=True)
    
    # 为每一帧生成YAML
    for i, raw_file in enumerate(raw_files):
        # 基础配置
        yaml_config = {
            'Black_level': float(BLACK_LEVEL),
            'White_level': float(WHITE_LEVEL),
            'ccm_matrix': [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
            'bayer_pattern': BAYER_PATTERN,
            'resolution': f"{IMAGE_WIDTH}x{IMAGE_HEIGHT}",
            'bit_depth': BIT_DEPTH
        }
        
        # 添加帧特定元数据
        if i in frames_meta:
            frame_meta = frames_meta[i]
            yaml_config.update(frame_meta)
        
        # 生成YAML文件名
        yaml_filename = f"{str(i).zfill(3)}.yaml"
        yaml_path = os.path.join(yaml_output_dir, yaml_filename)
        
        # 写入YAML文件
        try:
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(yaml_config, f, allow_unicode=True, sort_keys=False, 
                             default_flow_style=False)
        except Exception as e:
            print(f"  ❌ 写入失败 {yaml_filename}: {e}")
            continue
        
        # 进度显示
        if (i + 1) % 10 == 0 or (i + 1) == len(raw_files):
            print(f"    已生成: {i + 1}/{len(raw_files)} 个YAML文件")
    
    print(f"  ✅ 完成: {unpack_scene} - 生成 {len(raw_files)} 个YAML文件")


def main():
    """主函数"""
    print("=" * 70)
    print(" ISP YAML配置文件生成器 ")
    print("=" * 70)
    print(f"ROOT目录: {ROOT}")
    print(f"输入: {RECEIVED}")
    print(f"输出: {YAML_OUTPUT}")
    print("=" * 70)
    
    # 检查目录
    if not os.path.exists(RECEIVED):
        print(f"❌ 错误: 找不到received目录: {RECEIVED}")
        return
    
    if not os.path.exists(UNPACK_RAW):
        print(f"❌ 错误: 找不到unpack_raw目录: {UNPACK_RAW}")
        return
    
    # 获取场景映射
    scene_mapping = get_scene_mapping()
    
    if not scene_mapping:
        print("❌ 错误: 未找到有效的场景映射关系")
        print("   请确保received和unpack_raw目录下有对应的场景文件夹")
        return
    
    print(f"\n找到 {len(scene_mapping)} 个场景需要处理\n")
    
    # 处理每个场景
    for received_scene, unpack_scene in sorted(scene_mapping.items()):
        try:
            generate_yaml_for_scene(received_scene, unpack_scene)
        except Exception as e:
            print(f"❌ 处理场景 {received_scene} 时出错: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print(" 所有场景处理完成！")
    print("=" * 70)


if __name__ == '__main__':
    main()