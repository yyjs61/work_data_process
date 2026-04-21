#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据 received/<scene>/meta.txt 生成 yamls_eachFrame/<scene>/*.yaml
支持 DCG+LOFIC 双曝光参数（LOFIC 参数带 under_ 前缀）
同一个场景下所有 RAW 文件共用相同的 YAML 内容

ISO计算公式：ISO = gain × 100
exposure_ratio = 感度比
"""
import os
import re
import yaml
import natsort
from pathlib import Path


# ==================== 路径配置 ====================
ROOT = r"D:\Data\DJI_OV50X\20260420\20260417_portrait/"
# ROOT = "/path/to/your/project"  # Linux/Mac 路径示例

UNPACK_RAW = os.path.join(ROOT, 'unpack_raw')
RECEIVED_ROOT = os.path.join(ROOT, 'received')
YAML_OUTPUT_ROOT = os.path.join(ROOT, 'yamls_eachFrame')

# 曝光时间配置（单位：ns）
EXPOTIME_NS = 33000000  # 33.33ms

# ==================== 解析函数 ====================

def parse_meta_txt(meta_path: str) -> dict:
    """解析 meta.txt，返回字典"""
    meta = {}
    with open(meta_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line:
                continue
            key, val = line.split(':', 1)
            meta[key.strip()] = val.strip()
    return meta


def map_meta_to_yaml(meta: dict, expotime_ns: int) -> dict:
    """
    将 meta.txt 映射为 ISP YAML 结构
    DCG 参数：默认命名
    LOFIC 参数：加 under_ 前缀
    
    ISO = gain × 100
    exposure_ratio = 感度比
    """
    # 1. 解析尺寸
    size_match = re.search(r'(\d+)x(\d+)', meta.get('size', '4096x2304'))
    w, h = int(size_match.group(1)), int(size_match.group(2)) if size_match else (4096, 2304)

    # 2. 解析 WB 增益 [R, B]
    wb_match = re.search(r'\[([\d.]+),\s*([\d.]+)\]', meta.get('wbgain', '[2.0,2.0]'))
    r_gain = float(wb_match.group(1)) if wb_match else 2.0
    b_gain = float(wb_match.group(2)) if wb_match else 2.0

    # 3. 解析 DCG 参数（主曝光）
    dcg_bl = float(meta.get('DCG 14bit blacklevel', 1024))
    dcg_again = float(meta.get('dcg again', 1.0))
    exposure_ratio = float(meta.get('感度比', 1.0))  # 直接使用感度比
    
    # 4. 解析 LOFIC 参数（under 曝光）
    lofic_bl = float(meta.get('Lofic 14bit blacklevel', 4096))
    lofic_again = float(meta.get('lofic again', 1.0))
    
    # 5. 解析 CCT
    cct_match = re.search(r'(\d+)', meta.get('CCT', '5000K'))
    cct = int(cct_match.group(1)) if cct_match else 5000

    # 6. 计算 ISO（ISO = gain × 100）
    dcg_iso = dcg_again * 100.0
    lofic_iso = lofic_again * 100.0

    # 7. 构建 YAML 字典
    yaml_cfg = {
        # ========== 传感器基础参数 ==========
        # 'Black_level': dcg_bl,
        'Black_level': 256.0,
        'White_level': 16383.0,  # 14bit 最大值
        'under_Black_level': 256.0,
        'under_White_level': 4095.0,
        'bayer_pattern': meta.get('bayer pattern', 'BGGR').strip(),
        'ccm_matrix': [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]],
        
        # ========== 辅助参数 ==========
        'lux_index': 300.0,
        'luxid': 300.0,
        'cct': cct,
        
        # ========== DCG 参数（主曝光）==========
        'SensorAGain': dcg_again,
        'SensorDGain': 1.0,
        'expotime': expotime_ns,
        'gain': dcg_again,
        'iso': dcg_iso,  # ISO = gain × 100
        'isp_gain': 1.0,
        'sensorgain': dcg_again,
        'exposure_ratio': exposure_ratio,  # 直接使用感度比
        
        # ========== LOFIC 参数（under 曝光）==========
        'under_SensorAGain': lofic_again,
        'under_SensorDGain': 1.0,
        'under_expotime': expotime_ns,
        'under_gain': lofic_again,
        'under_iso': lofic_iso,  # under_ISO = under_gain × 100
        'under_sensorgain': lofic_again,
        
        # ========== 白平衡参数 ==========
        'r_gain': r_gain,
        'b_gain': b_gain,
    }
    
    return yaml_cfg


def generate_scene_yamls(scene: str, yaml_cfg: dict):
    """
    为单个场景生成所有帧的 YAML
    同一个场景下所有 YAML 内容相同
    """
    scene_path = os.path.join(UNPACK_RAW, scene)
    yaml_folder = os.path.join(YAML_OUTPUT_ROOT, scene)
    
    # 检查 RAW 目录是否存在
    if not os.path.exists(scene_path):
        print(f"⚠️  {scene}: 未找到目录 {scene_path}，跳过")
        return
    
    # 获取该场景下所有 raw 文件
    raw_files = [f for f in os.listdir(scene_path) if f.endswith('.raw')]
    if not raw_files:
        print(f"⚠️  {scene} 下未找到 .raw 文件，跳过")
        return
    
    raw_files = natsort.natsorted(raw_files)
    
    # 创建 YAML 输出目录
    os.makedirs(yaml_folder, exist_ok=True)
    
    # 为每个 raw 生成相同内容的 YAML
    for idx, raw_name in enumerate(raw_files):
        yaml_filename = f"{idx:03d}.yaml"
        yaml_path = os.path.join(yaml_folder, yaml_filename)
        
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(yaml_cfg, f, default_flow_style=None, 
                          allow_unicode=True, sort_keys=False)
        
        if idx == 0:  # 只打印第一个文件的详细信息
            print(f"✅ 场景: {scene}")
            print(f"   RAW 文件: {raw_name}")
            print(f"   DCG: ISO={yaml_cfg['iso']:.1f} (gain={yaml_cfg['SensorAGain']}×100), "
                  f"exposure_ratio={yaml_cfg['exposure_ratio']}")
            print(f"   LOFIC: under_ISO={yaml_cfg['under_iso']:.1f} (under_gain={yaml_cfg['under_SensorAGain']}×100)")
    
    print(f"📦 共生成 {len(raw_files)} 个 YAML 文件（内容相同）\n")


def main():
    """主函数"""
    # 验证目录
    if not os.path.exists(UNPACK_RAW):
        raise FileNotFoundError(f"❌ 未找到 unpack_raw 目录: {UNPACK_RAW}")
    if not os.path.exists(RECEIVED_ROOT):
        raise FileNotFoundError(f"❌ 未找到 received 目录: {RECEIVED_ROOT}")
    
    # 创建 YAML 输出根目录
    os.makedirs(YAML_OUTPUT_ROOT, exist_ok=True)
    
    print("=" * 70)
    print("🔧 ISP YAML 生成工具 (DCG+LOFIC 双曝光)")
    print("=" * 70)
    print(f"📁 项目根目录: {ROOT}")
    print(f"📁 RAW 目录: {UNPACK_RAW}")
    print(f"📁 Received 目录: {RECEIVED_ROOT}")
    print(f"📁 YAML 输出目录: {YAML_OUTPUT_ROOT}")
    print(f"⏱️  曝光时间: {EXPOTIME_NS} ns ({EXPOTIME_NS/1e6:.2f} ms)")
    print("=" * 70 + "\n")
    
    # 获取所有场景（自然排序）
    scenes = natsort.natsorted(os.listdir(UNPACK_RAW))
    
    if not scenes:
        print("❌ 未找到任何场景目录！")
        return
    
    print(f"📂 找到 {len(scenes)} 个场景\n")
    
    # 遍历所有场景
    scene_count = 0
    for scene in scenes:
        scene_path = os.path.join(UNPACK_RAW, scene)
        
        # 跳过非目录
        if not os.path.isdir(scene_path):
            continue
        
        # 查找对应的 meta.txt
        meta_file = os.path.join(RECEIVED_ROOT, scene.split("__")[1], 'meta.txt')
        if not os.path.exists(meta_file):
            print(f"⚠️  {scene}: 缺少 meta.txt ({meta_file})，跳过")
            continue
        
        scene_count += 1
        print(f"🔍 处理场景 [{scene_count}/{len(scenes)}]: {scene}")
        
        try:
            # 解析 meta.txt
            meta = parse_meta_txt(meta_file)
            
            # 映射为 YAML 配置
            yaml_cfg = map_meta_to_yaml(meta, EXPOTIME_NS)
            
            # 生成 YAML 文件
            generate_scene_yamls(scene, yaml_cfg)
            
        except Exception as e:
            print(f"❌ {scene}: 处理失败 - {e}\n")
            continue
    
    print("=" * 70)
    print(f"  全部完成！共处理 {scene_count} 个场景")
    print(f"📂 YAML 输出目录: {YAML_OUTPUT_ROOT}")
    print("=" * 70)


if __name__ == '__main__':
    main()