import os
import glob
import re
import numpy as np
import natsort

# --- 配置参数 ---
# ROOT = r"D:\Data\2026_06\04\030_4k60_quad_scg_outside_20260604"
# ROOT = r"D:\Data\2026_06\05\20260604_2x_4k60_raw\030_4k60_quad_scg_day_20260605"
ROOT = r"D:\Data\2026_06\13\030_4K60_2x_scg_self_testing_20260612/"

RECEIVED = os.path.join(ROOT, "received")
UNPACK_RAW = os.path.join(ROOT, "unpack_raw")
YAML_ROOT = os.path.join(ROOT, "yamls_eachFrame")
os.makedirs(YAML_ROOT, exist_ok=True)

# RAW 图像处理相关常量
BLACK_LEVEL = 64.0
WHITE_LEVEL = 1023.0
# WHITE_LEVEL = 16383.0
BAYER_PATTERN = 'BGGR'
HEIGHT = 2304
WIDTH = 4096

EXAMPLE_META = '''
Black_level: 64.0
White_level: 1023.0
bayer_pattern: BGGR
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
'''

def parse_meta_info_file(meta_file_path):
    """
    解析 meta_info txt 文件
    返回一个列表，每个元素是一个字典，包含该帧的所有 meta 信息
    """
    meta_list = []
    
    if not os.path.exists(meta_file_path):
        print(f"警告: meta 文件不存在: {meta_file_path}")
        return meta_list
    
    with open(meta_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 解析行，例如：
        # 1. shutter0.91ms_again1.01x_dgain1.00x_drcgain2.30x_luxindex110_wbgain[2.294189453125, 1, 1.71044921875]
        
        meta = {}
        
        # 提取 shutter (expotime)
        shutter_match = re.search(r'shutter([\d.]+)ms', line)
        if shutter_match:
            shutter_ms = float(shutter_match.group(1))
            meta['expotime'] = int(shutter_ms * 1000000)  # 转换为微秒
        else:
            meta['expotime'] = 10000  # 默认值
        
        # 提取 again (gain)
        again_match = re.search(r'again([\d.]+)x', line)
        if again_match:
            gain = float(again_match.group(1))
            meta['gain'] = gain
            meta['SensorAGain'] = gain
            meta['sensorgain'] = gain
        else:
            meta['gain'] = 1.0
            meta['SensorAGain'] = 1.0
            meta['sensorgain'] = 1.0
        
        # 提取 dgain (SensorDGain)
        dgain_match = re.search(r'dgain([\d.]+)x', line)
        if dgain_match:
            meta['SensorDGain'] = float(dgain_match.group(1))
        else:
            meta['SensorDGain'] = 1.0
        
        # 提取 drcgain
        drcgain_match = re.search(r'drcgain([\d.]+)x', line)
        if drcgain_match:
            meta['drc_gain'] = float(drcgain_match.group(1))
        else:
            meta['drc_gain'] = 1.0
        
        # 提取 luxindex
        luxindex_match = re.search(r'luxindex(\d+)', line)
        if luxindex_match:
            lux_index = int(luxindex_match.group(1))
            meta['lux_index'] = lux_index
            meta['luxid'] = lux_index
        else:
            meta['lux_index'] = 0
            meta['luxid'] = 0
        
        # 提取 wbgain [r_gain, g_gain, b_gain]
        wbgain_match = re.search(r'wbgain\[([\d.,\s]+)\]', line)
        if wbgain_match:
            wbgain_str = wbgain_match.group(1)
            wbgain_values = [float(x.strip()) for x in wbgain_str.split(',')]
            if len(wbgain_values) >= 3:
                meta['r_gain'] = wbgain_values[0]
                meta['g_gain'] = wbgain_values[1]
                meta['b_gain'] = wbgain_values[2]
            elif len(wbgain_values) == 2:
                meta['r_gain'] = wbgain_values[0]
                meta['g_gain'] = 1.0
                meta['b_gain'] = wbgain_values[1]
            else:
                meta['r_gain'] = 1.0
                meta['g_gain'] = 1.0
                meta['b_gain'] = 1.0
        else:
            meta['r_gain'] = 1.0
            meta['g_gain'] = 1.0
            meta['b_gain'] = 1.0
        
        meta_list.append(meta)
    
    return meta_list

def get_awb_gain_from_raw(raw_file_path):
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
        
        scale_r = max(1.0, sum_g / 2 / sum_r) if sum_r > 0 else 1.0
        scale_b = max(1.0, sum_g / 2 / sum_b) if sum_b > 0 else 1.0
        return scale_r, scale_b
    except:
        return 1.0, 1.0

H = HEIGHT
W = WIDTH

def quad_bayer_to_raw(quad_bayer):
    quad_bayer = np.fromfile(quad_bayer, dtype=np.uint16).reshape([H, W]).astype(float)
    '''
    G R  g1 g2
    B G  g3 g4
    '''
    raw = np.zeros([quad_bayer.shape[0]//2, quad_bayer.shape[1]//2], dtype=np.uint16).astype(float)
    g1_1 = quad_bayer[::4, ::4]
    g1_2 = quad_bayer[::4, 1::4]
    g1_3 = quad_bayer[1::4, ::4]
    g1_4 = quad_bayer[1::4, 1::4]
    raw[::2, ::2] = (g1_1 + g1_2 + g1_3 + g1_4) / 4

    r1 = quad_bayer[::4, 2::4]
    r2 = quad_bayer[::4, 3::4]
    r3 = quad_bayer[1::4, 2::4]
    r4 = quad_bayer[1::4, 3::4]
    raw[::2, 1::2] = (r1 + r2 + r3 + r4) / 4

    b1 = quad_bayer[2::4, ::4]
    b2 = quad_bayer[2::4, 1::4]
    b3 = quad_bayer[3::4, ::4]
    b4 = quad_bayer[3::4, 1::4]
    raw[1::2, ::2] = (b1 + b2 + b3 + b4) / 4

    g2_1 = quad_bayer[2::4, 2::4]
    g2_2 = quad_bayer[2::4, 3::4]
    g2_3 = quad_bayer[3::4, 2::4]
    g2_4 = quad_bayer[3::4, 3::4]
    raw[1::2, 1::2] = (g2_1 + g2_2 + g2_3 + g2_4) / 4

    return raw.astype(np.uint16)

# --- 解析 meta_info txt 文件 ---
# 查找 received 目录下的 meta_info txt 文件
meta_files = glob.glob(os.path.join(RECEIVED, "meta_info*.txt"))
if meta_files:
    meta_file_path = meta_files[0]
    print(f"找到 meta 文件: {meta_file_path}")
    frames_meta = parse_meta_info_file(meta_file_path)
    print(f"解析到 {len(frames_meta)} 帧的 meta 信息")
else:
    print("警告: 未找到 meta_info txt 文件，将使用默认值")
    frames_meta = []

# --- 遍历 unpack_raw 文件夹 ---
scenes = natsort.natsorted(os.listdir(UNPACK_RAW))
meta_index = 0  # 用于追踪当前使用哪个 meta 信息

for scene in scenes:
    raw_scene_dir = os.path.join(UNPACK_RAW, scene)
    if not os.path.isdir(raw_scene_dir):
        continue
    
    # --- 1. 从文件夹名提取参数 (处理 3p3x 这种格式) ---
    def extract_val(pattern, string, default=1.0):
        # 匹配数字和字母 'p'，例如 again3p3x
        match = re.search(pattern, string, re.IGNORECASE)
        if match:
            val_str = match.group(1).replace('p', '.')  # 将 '3p3' 换成 '3.3'
            try:
                return float(val_str)
            except:
                return default
        return default

    f_again = extract_val(r"again([\dp\.]+)x", scene, 1.0)
    f_ispd = extract_val(r"ispdgain([\dp\.]+)x", scene, 1.0)
    f_drc = extract_val(r"drcgain([\dp\.]+)x", scene, 1.0)
    
    # 获取当前场景的 meta 信息（如果有的话）
    current_meta = frames_meta[meta_index] if meta_index < len(frames_meta) else {}
    
    raw_files = natsort.natsorted(glob.glob(os.path.join(raw_scene_dir, "*.raw")))
    if not raw_files:
        continue
    
    out_scene_path = os.path.join(YAML_ROOT, scene)
    os.makedirs(out_scene_path, exist_ok=True)
    
    # 计算 raw 文件的 AWB gain（作为备用）
    raw_awb_r, raw_awb_b = get_awb_gain_from_raw(quad_bayer_to_raw(raw_files[0]))
    
    for i in range(len(raw_files)):
        yaml_path = os.path.join(out_scene_path, f"{str(i).zfill(3)}.yaml")
        
        # 优先使用 meta_info txt 中的信息，如果没有则使用从文件夹名提取的或默认值
        expotime = current_meta.get('expotime', 10000)
        gain = current_meta.get('gain', f_again)
        sensor_a_gain = current_meta.get('SensorAGain', f_again)
        sensor_gain = current_meta.get('sensorgain', f_again)
        sensor_d_gain = current_meta.get('SensorDGain', 1.0)
        drc_gain = current_meta.get('drc_gain', f_drc)
        lux_index = current_meta.get('lux_index', 0)
        luxid = current_meta.get('luxid', 0)
        r_gain = current_meta.get('r_gain', raw_awb_r)
        b_gain = current_meta.get('b_gain', raw_awb_b)
        cct = current_meta.get('cct', 4000)
        iso = int(gain * 100.0)  # 假设转换比例
        
        with open(yaml_path, "w") as fo:
            fo.write(EXAMPLE_META)
            fo.write(f"gain: {gain:.4f}\n")
            fo.write(f"SensorAGain: {sensor_a_gain:.4f}\n")
            fo.write(f"sensorgain: {sensor_gain:.4f}\n")
            fo.write(f"SensorDGain: {sensor_d_gain:.4f}\n")
            fo.write(f"iso: {iso}\n")
            fo.write(f"expotime: {expotime}\n")
            fo.write(f"isp_gain: {f_ispd:.4f}\n")
            fo.write(f"cct: {cct}\n")
            fo.write(f"r_gain: {r_gain:.4f}\n")
            fo.write(f"b_gain: {b_gain:.4f}\n")
            fo.write(f"drc_gain: {drc_gain:.4f}\n")
            fo.write(f"lux_index: {lux_index}\n")
            fo.write(f"luxid: {luxid}\n")
    
    # 打印场景信息
    if current_meta:
        print(f"[OK] {scene} -> exp:{current_meta.get('expotime', 'N/A')}, "
              f"gain:{current_meta.get('gain', 'N/A')}, "
              f"drc:{current_meta.get('drc_gain', 'N/A')}, "
              f"lux:{current_meta.get('lux_index', 'N/A')}, "
              f"r_gain:{current_meta.get('r_gain', 'N/A')}, "
              f"b_gain:{current_meta.get('b_gain', 'N/A')}")
    else:
        print(f"[OK] {scene} -> 使用默认值 (again:{f_again}, ispd:{f_ispd}, drc:{f_drc})")
    
    # 移动到下一个 meta 信息
    meta_index += 1

print(f"\n处理完成！共处理 {len(scenes)} 个场景")