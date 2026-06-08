import os
import glob
import re
import numpy as np
import natsort

# --- 配置参数 ---
# ROOT = "/data/030_raw_contrast_20260508"
# ROOT = r"D:\Data\2026_05\13\030_dcg_lab_20260508/"
# ROOT = r"D:\Data\2026_06\01\wb_stats_0529/"
ROOT = r"D:\Data\2026_06\05\030_1x_dcg_sensor_raw_ev0_ev+_ev+2_3000k_20260605/"
ROOT = r"D:\Data\2026_06\05\030_2x_4k30_quad_dcg_day_20260605/"

RECEIVED = os.path.join(ROOT, "received")
UNPACK_RAW = os.path.join(ROOT, "unpack_raw")
YAML_ROOT = os.path.join(ROOT, "yamls_eachFrame")

os.makedirs(YAML_ROOT, exist_ok=True)

# RAW 图像处理相关常量
# BLACK_LEVEL = 64.0
WHITE_LEVEL = 16383.0
BLACK_LEVEL = 64.0
# WHITE_LEVEL = 1023.0
BAYER_PATTERN = 'BGGR' 
HEIGHT = 2304
WIDTH = 4096

EXAMPLE_META = '''
Black_level: 64.0
White_level: 16383.0
bayer_pattern: BGGR
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
'''

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
    quad_bayer = np.fromfile(quad_bayer,dtype=np.uint16).reshape([H,W]).astype(float)
    '''
        G R  g1 g2    
        B G  g3 g4
    '''
    raw = np.zeros([quad_bayer.shape[0]//2,quad_bayer.shape[1]//2],dtype=np.uint16).astype(float)

    g1_1 = quad_bayer[::4,::4]
    g1_2 = quad_bayer[::4,1::4]
    g1_3 = quad_bayer[1::4,::4]
    g1_4 = quad_bayer[1::4,1::4]
    raw[::2,::2] = (g1_1 + g1_2 + g1_3 + g1_4)/4

    r1 = quad_bayer[::4,2::4]
    r2 = quad_bayer[::4,3::4]
    r3 = quad_bayer[1::4,2::4]
    r4 = quad_bayer[1::4,3::4]
    raw[::2,1::2] = (r1 + r2 + r3 + r4)/4

    b1 = quad_bayer[2::4,::4]
    b2 = quad_bayer[2::4,1::4]
    b3 = quad_bayer[3::4,::4]
    b4 = quad_bayer[3::4,1::4]
    raw[1::2,::2] = (b1 + b2 + b3 + b4)/4

    g2_1 = quad_bayer[2::4,2::4]
    g2_2 = quad_bayer[2::4,3::4]
    g2_3 = quad_bayer[3::4,2::4]
    g2_4 = quad_bayer[3::4,3::4]
    raw[1::2,1::2] = (g2_1 + g2_2 + g2_3 + g2_4)/4

    return raw.astype(np.uint16)

def parse_srt(srt_path):
    # 此处保留原有的 SRT 解析逻辑，用于提取曝光时间、CCT 等其他参数
    # 如果没有 SRT，后续会使用默认值
    return [] # 简化示例，实际请保留你代码中的 parse_srt 和 parse_font_line

# 遍历 unpack_raw 文件夹
scenes = natsort.natsorted(os.listdir(UNPACK_RAW))

for scene in scenes:
    raw_scene_dir = os.path.join(UNPACK_RAW, scene)
    if not os.path.isdir(raw_scene_dir): continue

    # --- 1. 从文件夹名提取参数 (处理 3p3x 这种格式) ---
    def extract_val(pattern, string, default=1.0):
        # 匹配数字和字母 'p'，例如 again3p3x
        match = re.search(pattern, string, re.IGNORECASE)
        if match:
            val_str = match.group(1).replace('p', '.') # 将 '3p3' 换成 '3.3'
            try:
                return float(val_str)
            except:
                return default
        return default

    f_again = extract_val(r"again([\dp\.]+)x", scene, 1.4)
    f_ispd = extract_val(r"ispdgain([\dp\.]+)x", scene, 1.0)
    f_drc = extract_val(r"drcgain([\dp\.]+)x", scene, 1.0)

    # 匹配对应的 received 目录获取 SRT
    recv_scene_name = re.sub(r"^\d+__", "", scene)
    recv_scene_dir = os.path.join(RECEIVED, recv_scene_name)
    
    raw_files = natsort.natsorted(glob.glob(os.path.join(raw_scene_dir, "*.raw")))
    if not raw_files: continue

    srt_files = glob.glob(os.path.join(recv_scene_dir, "*.SRT"))
    frames_meta = parse_srt(srt_files[0]) if srt_files else []

    out_scene_path = os.path.join(YAML_ROOT, scene)
    os.makedirs(out_scene_path, exist_ok=True)

    raw_awb_r, raw_awb_b = get_awb_gain_from_raw(quad_bayer_to_raw(raw_files[0]))
    # raw_awb_r, raw_awb_b = get_awb_gain_from_raw(raw_files[0])

    for i in range(len(raw_files)):
        meta = frames_meta[i] if i < len(frames_meta) else {}
        yaml_path = os.path.join(out_scene_path, f"{str(i).zfill(3)}.yaml")

        # 增益与 ISO 逻辑
        gain = f_again
        iso = gain * 100.0 # 假设转换比例
        isp_gain = f_ispd
        drc_gain = f_drc
        
        # 其他从 SRT 或默认获取的参数
        expotime = int(meta.get("expotime_s", 0.01) * 1e6)
        r_gain = meta.get("r_gain", raw_awb_r)
        b_gain = meta.get("b_gain", raw_awb_b)
        cct = int(meta.get("cct", 4000))
        lux_index = int(meta.get("lux_index", 300))

        with open(yaml_path, "w") as fo:
            fo.write(EXAMPLE_META)
            fo.write(f"gain: {gain:.4f}\n")
            fo.write(f"SensorAGain: {gain:.4f}\n")
            fo.write(f"sensorgain: {gain:.4f}\n")
            fo.write(f"SensorDGain: 1.00\n")
            fo.write(f"iso: {int(iso)}\n")
            fo.write(f"expotime: {expotime}\n")
            fo.write(f"isp_gain: 1.00\n")
            fo.write(f"cct: {cct}\n")
            fo.write(f"r_gain: {r_gain:.4f}\n")
            fo.write(f"b_gain: {b_gain:.4f}\n")
            fo.write(f"drc_gain: 1.00\n")
            fo.write(f"lux_index: {lux_index}\n")
            fo.write(f"luxid: {lux_index}\n")

    print(f"[OK] {scene} -> again:{f_again}, ispd:{f_ispd}, drc:{f_drc}")