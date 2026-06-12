import os
import glob
import re
import numpy as np
import natsort

# --- 配置参数 ---
ROOT = r"D:\Data\2026_06\10\SC532_SCG_10bit_ISP_simulation_demo_raw_20260610"
RECEIVED = os.path.join(ROOT, "received")
UNPACK_RAW = os.path.join(ROOT, "unpack_raw")
YAML_ROOT = os.path.join(ROOT, "yamls_eachFrame")
os.makedirs(YAML_ROOT, exist_ok=True)

# --- RAW 图像处理相关常量 ---
BLACK_LEVEL = 64.0
WHITE_LEVEL = 1023.0
BAYER_PATTERN = 'BGGR'
HEIGHT = 2160
WIDTH = 3840

EXAMPLE_META = '''Black_level: 64.0
White_level: 1023.0
bayer_pattern: BGGR
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
'''

def parse_raw_filename(filename):
    """
    从raw文件名中解析meta信息
    例如: 000__cam0_3840x2160_10bit_rggb_20260609_145452_exp1008us_gain100_frameID2726_001.raw
    返回: {'exp': 1008, 'gain': 100, 'frameID': 2726, ...}
    """
    basename = os.path.basename(filename)
    
    # 解析exp时间 (exp1008us)
    exp_match = re.search(r'exp(\d+)us', basename, re.IGNORECASE)
    exp_us = int(exp_match.group(1)) if exp_match else 1000  # 默认1000us
    
    # 解析gain (gain100)
    gain_match = re.search(r'gain(\d+)', basename, re.IGNORECASE)
    gain = int(gain_match.group(1)) if gain_match else 100  # 默认100
    
    # 解析frameID
    frameid_match = re.search(r'frameID(\d+)', basename, re.IGNORECASE)
    frame_id = int(frameid_match.group(1)) if frameid_match else 0
    
    # 解析分辨率 (3840x2160)
    res_match = re.search(r'(\d+)x(\d+)', basename)
    if res_match:
        width = int(res_match.group(1))
        height = int(res_match.group(2))
    else:
        width = WIDTH
        height = HEIGHT
    
    # 解析bit位 (10bit)
    bit_match = re.search(r'(\d+)bit', basename, re.IGNORECASE)
    bit_depth = int(bit_match.group(1)) if bit_match else 10
    
    # 解析bayer格式 (rggb/bggr/grbg/gbrg)
    bayer_match = re.search(r'_(rggb|bggr|grbg|gbrg)_', basename, re.IGNORECASE)
    bayer = bayer_match.group(1).upper() if bayer_match else 'RGGB'
    
    return {
        'exp_us': exp_us,
        'gain': gain,
        'frameID': frame_id,
        'width': width,
        'height': height,
        'bit_depth': bit_depth,
        'bayer': bayer
    }

def get_awb_gain_from_raw(raw_file_path):
    """从raw文件计算AWB增益"""
    try:
        raw_data = np.fromfile(raw_file_path, dtype=np.uint16)
        img = raw_data.reshape(HEIGHT, WIDTH).astype(float)
        img = (img - BLACK_LEVEL) / (WHITE_LEVEL - BLACK_LEVEL)
        img = img.clip(0, 1)
        
        if BAYER_PATTERN == 'BGGR':
            sum_b = np.sum(img[0::2, 0::2])
            sum_r = np.sum(img[1::2, 1::2])
            sum_g = np.sum(img[0::2, 1::2]) + np.sum(img[1::2, 0::2])
        elif BAYER_PATTERN == 'RGGB':
            sum_r = np.sum(img[0::2, 0::2])
            sum_b = np.sum(img[1::2, 1::2])
            sum_g = np.sum(img[0::2, 1::2]) + np.sum(img[1::2, 0::2])
        else:  # 其他bayer格式
            sum_r = np.sum(img[0::2, 0::2])
            sum_b = np.sum(img[1::2, 1::2])
            sum_g = np.sum(img[0::2, 1::2]) + np.sum(img[1::2, 0::2])
        
        scale_r = max(1.0, sum_g / 2 / sum_r) if sum_r > 0 else 1.0
        scale_b = max(1.0, sum_g / 2 / sum_b) if sum_b > 0 else 1.0
        
        return scale_r, scale_b
    except Exception as e:
        print(f"  Warning: 计算AWB失败: {e}")
        return 1.0, 1.0

# --- 遍历 unpack_raw 文件夹 ---
scenes = natsort.natsorted(os.listdir(UNPACK_RAW))

for scene in scenes:
    raw_scene_dir = os.path.join(UNPACK_RAW, scene)
    if not os.path.isdir(raw_scene_dir):
        continue
    
    print(f"\n处理场景: {scene}")
    
    # 获取所有raw文件
    raw_files = natsort.natsorted(glob.glob(os.path.join(raw_scene_dir, "*.raw")))
    
    if not raw_files:
        print(f"  跳过: 没有找到raw文件")
        continue
    
    # 从第一个raw文件解析meta信息
    first_raw = raw_files[0]
    meta_info = parse_raw_filename(first_raw)
    
    print(f"  从文件名解析: exp={meta_info['exp_us']}us, gain={meta_info['gain']}, "
          f"bayer={meta_info['bayer']}, resolution={meta_info['width']}x{meta_info['height']}")
    
    # 计算AWB增益（从第一个raw文件）
    raw_awb_r, raw_awb_b = get_awb_gain_from_raw(first_raw)
    print(f"  计算AWB: r_gain={raw_awb_r:.4f}, b_gain={raw_awb_b:.4f}")
    
    # 创建输出目录
    out_scene_path = os.path.join(YAML_ROOT, scene)
    os.makedirs(out_scene_path, exist_ok=True)
    
    # gain转换为浮点数（假设gain100表示1.0）
    gain_float = meta_info['gain'] / 100.0
    iso = meta_info['gain']  # 假设gain值就是ISO
    
    # 为每个raw文件生成yaml
    for i, raw_file in enumerate(raw_files):
        yaml_path = os.path.join(out_scene_path, f"{str(i).zfill(3)}.yaml")
        
        # 如果需要，也可以从每个文件名解析（这里使用第一个文件的参数）
        # file_meta = parse_raw_filename(raw_file)
        
        with open(yaml_path, "w") as fo:
            fo.write(EXAMPLE_META)
            fo.write(f"gain: {gain_float:.4f}\n")
            fo.write(f"SensorAGain: {gain_float:.4f}\n")
            fo.write(f"sensorgain: {gain_float:.4f}\n")
            fo.write(f"SensorDGain: 1.0000\n")
            fo.write(f"iso: {iso}\n")
            # fo.write(f"expotime: {meta_info['exp_us']}\n")
            fo.write(f"expotime: 16600000\n")
            fo.write(f"isp_gain: 1.0000\n")
            fo.write(f"cct: 4000\n")  # 默认值
            fo.write(f"r_gain: {raw_awb_r:.4f}\n")
            fo.write(f"b_gain: {raw_awb_b:.4f}\n")
            fo.write(f"drc_gain: 1.0000\n")
            fo.write(f"lux_index: 300\n")  # 默认值
            fo.write(f"luxid: 300\n")
            fo.write(f"frameID: {meta_info['frameID'] + i}\n")
    
    print(f"  完成: 生成 {len(raw_files)} 个yaml文件 -> {out_scene_path}")

print("\n=== 所有场景处理完成 ===")