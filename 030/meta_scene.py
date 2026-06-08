import os
import glob
import yaml
import re
import natsort
import numpy as np

ROOT = r'D:\Data\2026_06\01\030_wb_stats_20260529/'
UNPACK_RAW = os.path.join(ROOT, 'unpack_raw')
YAML_ROOT  = os.path.join(ROOT, 'yamls_eachFrame')

# 图像参数
BLACK_LEVEL = 64.0
WHITE_LEVEL = 16383.0
BAYER_PATTERN = 'BGGR'  # 根据您的bayer_pattern设置

# 图像尺寸（根据实际情况调整）
HEIGHT = 2304
WIDTH = 4096

EXAMPLE_META = '''
Black_level: 64.0
White_level: 16383.0
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
bayer_pattern: BGGR
'''

def convert_to_python_types(obj):
    """
    将numpy类型转换为Python原生类型，以便YAML序列化
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_python_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_python_types(item) for item in obj]
    else:
        return obj

def get_awb_gain(raw_file_path):
    """
    从raw文件中通过灰度世界算法计算AWB增益
    """
    # 读取raw文件
    raw_data = np.fromfile(raw_file_path, dtype=np.uint16)
    # 重塑为2D数组
    img = raw_data.reshape(HEIGHT, WIDTH).astype(float)

    # 归一化
    img = (img - BLACK_LEVEL) / (WHITE_LEVEL - BLACK_LEVEL)
    img = img.clip(0, 1)

    # 根据Bayer pattern计算各通道和
    if BAYER_PATTERN == 'RGGB':
        sum_r = np.sum(img[0::2, 0::2])
        sum_b = np.sum(img[1::2, 1::2])
        sum_g = np.sum(img[0::2, 1::2]) + np.sum(img[1::2, 0::2])
        
        scale_r = max(1.0,  sum_g / 2 / sum_r) if sum_r  > 0 else 1.0
        scale_b = max(1.0, sum_g / 2 / sum_b) if sum_b  > 0 else 1.0
        
    elif BAYER_PATTERN == 'GBRG':
        sum_r = np.sum(img[1::2, 0::2])
        sum_b = np.sum(img[0::2, 1::2])
        sum_g = np.sum(img[0::2, 0::2]) + np.sum(img[1::2, 1::2])
        
        scale_r = max(1.0, sum_g / 2 / sum_r) if sum_r  > 0 else 1.0
        scale_b = max(1.0, sum_g / 2 / sum_b) if sum_b  > 0 else 1.0
        
    elif BAYER_PATTERN == 'GRBG':
        sum_r = np.sum(img[0::2, 1::2])
        sum_b = np.sum(img[1::2, 0::2])
        sum_g = np.sum(img[0::2, 0::2]) + np.sum(img[1::2, 1::2])
        
        scale_r = max(1.0, sum_g / 2 / sum_r) if sum_r  > 0 else 1.0
        scale_b = max(1.0, sum_g / 2 / sum_b) if sum_b  > 0 else 1.0
        
    elif BAYER_PATTERN == 'BGGR':
        sum_r = np.sum(img[1::2, 1::2])
        sum_b = np.sum(img[0::2, 0::2])
        sum_g = np.sum(img[0::2, 1::2]) + np.sum(img[1::2, 0::2])
        
        scale_r = max(1.0, sum_g / 2 / sum_r) if sum_r  > 0 else 1.0
        scale_b = max(1.0, sum_g / 2 / sum_b) if sum_b  > 0 else 1.0

    else:
        raise ValueError(f"Unsupported Bayer pattern: {BAYER_PATTERN}")

    return scale_r, scale_b

def parse_scene_name(scene_name):
    """
    从场景文件夹名中提取ISO值
    支持格式如：
    00_A_dcg_4096x2304_16x9_video30_iso100
    01_A_dcg_4096x2304_16x9_video30_iso400
    06_CWF_dcg_4096x2304_16x9_video30_iso100
    12_HZ_dcg_4096x2304_16x9_video30_iso100
    """
    result = {}
    
    # =========================
    # 1. 提取 ISO 值
    # =========================
    iso_match = re.search(r'iso(\d+)', scene_name, re.IGNORECASE)
    if iso_match:
        iso = int(iso_match.group(1))
        result['iso'] = min(iso * 1.4, 1600)
        
        # 根据公式计算gain: min(iso * 1.4, 1600) / 100
        gain_value = min(iso * 1.4, 1600) / 100.0
        # gain_value = min(iso, 1600) / 100.0
        
        result['gain'] = gain_value
        result['sensorgain'] = gain_value
        result['SensorAGain'] = gain_value
    else:
        # 如果没有找到ISO，使用默认值
        print(f"  Warning: No ISO found in scene name '{scene_name}', using default ISO 100")
        result['iso'] = 100
        result['gain'] = 1.4
        result['sensorgain'] = 1.4
        result['SensorAGain'] = 1.4
    
    # =========================
    # 2. 默认参数
    # =========================
    result['expotime'] = 33000  # 默认曝光时间 33ms (单位: ns)
    result['cct'] = 5000  # 默认色温 5000K
    result['SensorDGain'] = 1.0
    result['isp_gain'] = 1.0
    result['drc_gain'] = 1.0
    result['lux_index'] = 400.0
    result['luxid'] = 400.0
    
    # AWB增益将在后面动态计算
    result['r_gain'] = 1.0
    result['b_gain'] = 1.0

    return result

# =========================
# 主流程
# =========================
if __name__ == "__main__":
    scenes = natsort.natsorted(
        [d for d in os.listdir(UNPACK_RAW)
         if os.path.isdir(os.path.join(UNPACK_RAW, d))]
    )
    
    for scene in scenes:
        print(f'\nProcessing scene: {scene}')
        raw_scene_path = os.path.join(UNPACK_RAW, scene)
        yaml_folder = os.path.join(YAML_ROOT, scene)
        os.makedirs(yaml_folder, exist_ok=True)

        raw_files = natsort.natsorted(
            glob.glob(os.path.join(raw_scene_path, '*.raw*'))
        )

        # 解析场景名获取基础参数（主要是ISO和gain）
        base_meta_info = parse_scene_name(scene)
        print(f"  ISO: {base_meta_info['iso']}, Gain: {base_meta_info['gain']:.3f}")

        # 使用第一帧图像计算AWB增益
        if len(raw_files) > 0:
            print(f"  Calculating AWB gains from first frame: {os.path.basename(raw_files[0])}")
            r_gain, b_gain = get_awb_gain(raw_files[0])
            print(f"  AWB gains: R={r_gain:.3f}, B={b_gain:.3f}")
            
            # 将计算出的AWB增益添加到meta信息中
            base_meta_info['r_gain'] = r_gain
            base_meta_info['b_gain'] = b_gain
        else:
            print(f"  Warning: No raw files found, using default AWB gains")
            base_meta_info['r_gain'] = 1.0
            base_meta_info['b_gain'] = 1.0

        # 转换numpy类型为Python原生类型
        base_meta_info = convert_to_python_types(base_meta_info)

        # 为每一帧生成yaml文件
        for idx in range(len(raw_files)):
            yaml_file = os.path.join(
                yaml_folder,
                f'{str(idx).zfill(3)}.yaml'
            )
            
            with open(yaml_file, 'w') as fo:
                fo.write(EXAMPLE_META)
                yaml.safe_dump(
                    base_meta_info,
                    stream=fo,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False  # 保持字段顺序
                )

        print(f"  Generated {len(raw_files)} yaml files")
    
    print("\nDone.")