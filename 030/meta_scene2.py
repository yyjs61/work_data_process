import os
import glob
import yaml
import re
import natsort
import numpy as np

# ROOT = 'D:/Data/2026_06/01/030_20260601_day_dump/'
ROOT = r'D:\Data\2026_06\05\030_2x_4k30_quad_dcg_day_20260605/'

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

def parse_value_with_p(value_str):
    """
    解析带'p'的数值，如 '1p50' -> 1.50, '1p00' -> 1.00
    """
    if 'p' in value_str:
        return float(value_str.replace('p', '.'))
    else:
        return float(value_str)

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
    解析场景名，支持格式如：
    1_shutter1p50ms_again1p00x_dgain1p00x_drcgain2p72x
    2_shutter10p00ms_again1p17x_dgain1p00x_drcgain1p12x
    """
    result = {}
    
    print(f"  Parsing scene name: {scene_name}")

    # =========================
    # 1. 提取曝光时间 (shutter)
    # =========================
    shutter_match = re.search(r'shutter([\d.]+p[\d.]+|\d+)ms', scene_name, re.IGNORECASE)
    if shutter_match:
        shutter_str = shutter_match.group(1)
        shutter_ms = parse_value_with_p(shutter_str)
        result['expotime'] = int(shutter_ms * 1_000_000)  # ms → ns
        print(f"  Shutter: {shutter_ms}ms -> expotime: {result['expotime']}ns")
    else:
        result['expotime'] = 33000  # 默认值 33ms
        print(f"  Warning: No shutter found, using default expotime: {result['expotime']}ns")

    # =========================
    # 2. 提取 again (analog gain)
    # =========================
    again_match = re.search(r'again([\d.]+p[\d.]+|\d+)x', scene_name, re.IGNORECASE)
    if again_match:
        again_str = again_match.group(1)
        again = parse_value_with_p(again_str)
        print(f"  Again: {again}")
    else:
        again = 1.0
        print(f"  Warning: No again found, using default again: {again}")
    
    # 计算 ISO
    iso = int(again * 100)
    result['iso'] = iso
    
    # 根据公式：gain = sensorgain = SensorAGain = iso / 100
    gain = iso / 100.0
    result['gain'] = gain
    result['SensorAGain'] = gain
    result['sensorgain'] = gain
    print(f"  ISO: {iso}, Gain: {gain}")

    # =========================
    # 3. 提取 dgain (digital gain)
    # =========================
    dgain_match = re.search(r'dgain([\d.]+p[\d.]+|\d+)x', scene_name, re.IGNORECASE)
    if dgain_match:
        dgain_str = dgain_match.group(1)
        dgain = parse_value_with_p(dgain_str)
        result['SensorDGain'] = dgain
        print(f"  Dgain: {dgain}")
    else:
        result['SensorDGain'] = 1.0
        print(f"  Warning: No dgain found, using default SensorDGain: {result['SensorDGain']}")

    # =========================
    # 4. 提取 drcgain
    # =========================
    drcgain_match = re.search(r'drcgain([\d.]+p[\d.]+|\d+)x', scene_name, re.IGNORECASE)
    if drcgain_match:
        drcgain_str = drcgain_match.group(1)
        drcgain = parse_value_with_p(drcgain_str)
        result['drc_gain'] = drcgain
        print(f"  Drcgain: {drcgain}")
    else:
        result['drc_gain'] = 1.0
        print(f"  Warning: No drcgain found, using default drc_gain: {result['drc_gain']}")

    # =========================
    # 5. 固定参数
    # =========================
    result['isp_gain'] = 1.0
    result['cct'] = 5000  # 默认色温 5000K
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

        # 解析场景名获取基础参数
        base_meta_info = parse_scene_name(scene)

        # 使用第一帧图像计算AWB增益
        if len(raw_files) > 0:
            print(f"  Calculating AWB gains from first frame: {os.path.basename(raw_files[0])}")
            r_gain, b_gain = get_awb_gain(raw_files[0])
            print(f"  AWB gains: R={r_gain:.3f}, B={b_gain:.3f}")
            
            # 将计算出的AWB增益添加到meta信息中
            base_meta_info['r_gain'] = r_gain
            base_meta_info['b_gain'] = b_gain
        else:
            # 如果没有raw文件，使用默认值
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