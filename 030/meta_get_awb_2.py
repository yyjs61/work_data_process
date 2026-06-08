import os
import glob
import re
import numpy as np
import natsort

# --- 配置参数 ---
# ROOT = "/data/030_2x_4k30_quad_dcg_night_20260605/"
ROOT = r"D:\Data\2026_06\05\030_2x_4k30_quad_dcg_day_20260605/"
RECEIVED = os.path.join(ROOT, "received")
UNPACK_RAW = os.path.join(ROOT, "unpack_raw")
YAML_ROOT = os.path.join(ROOT, "yamls_eachFrame")

os.makedirs(YAML_ROOT, exist_ok=True)

# --- 处理选项 ---
DO_QUAD_PROCESS = True  # 是否进行 Quad Bayer 到 Raw 的下采样转换
BLACK_LEVEL = 64.0
WHITE_LEVEL = 16383.0
BAYER_PATTERN = 'BGGR' 
HEIGHT = 2304
WIDTH = 4096

EXAMPLE_META = f'''
Black_level: {BLACK_LEVEL}
White_level: {WHITE_LEVEL}
bayer_pattern: {BAYER_PATTERN}
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
'''

def quad_bayer_to_raw(file_path):
    """ 将 Quad Bayer 格式下采样为标准 Bayer 格式 """
    # 读取并 Reshape
    quad_data = np.fromfile(file_path, dtype=np.uint16).reshape([HEIGHT, WIDTH]).astype(float)
    
    # 初始化下采样后的图像 (H/2, W/2)
    raw = np.zeros([HEIGHT // 2, WIDTH // 2], dtype=np.float32)

    # 按照 4x4 块结构提取并取平均 (适配你提供的逻辑)
    raw[::2, ::2] = (quad_data[0::4, 0::4] + quad_data[0::4, 1::4] + 
                     quad_data[1::4, 0::4] + quad_data[1::4, 1::4]) / 4.0
    raw[::2, 1::2] = (quad_data[0::4, 2::4] + quad_data[0::4, 3::4] + 
                      quad_data[1::4, 2::4] + quad_data[1::4, 3::4]) / 4.0
    raw[1::2, ::2] = (quad_data[2::4, 0::4] + quad_data[2::4, 1::4] + 
                      quad_data[3::4, 0::4] + quad_data[3::4, 1::4]) / 4.0
    raw[1::2, 1::2] = (quad_data[2::4, 2::4] + quad_data[2::4, 3::4] + 
                       quad_data[3::4, 2::4] + quad_data[3::4, 3::4]) / 4.0
    
    return raw

def calculate_awb_gain(img_data):
    """ 基于灰度世界算法计算 AWB 增益 """
    img = img_data.astype(float)
    img = (img - BLACK_LEVEL) / (WHITE_LEVEL - BLACK_LEVEL)
    img = img.clip(0, 1)
    
    eps = 1e-6 # 防止除零
    
    if BAYER_PATTERN == 'RGGB':
        sum_r = np.sum(img[0::2, 0::2])
        sum_b = np.sum(img[1::2, 1::2])
        sum_g = np.sum(img[0::2, 1::2]) + np.sum(img[1::2, 0::2])
    elif BAYER_PATTERN == 'GBRG':
        sum_r = np.sum(img[1::2, 0::2])
        sum_b = np.sum(img[0::2, 1::2])
        sum_g = np.sum(img[0::2, 0::2]) + np.sum(img[1::2, 1::2])
    elif BAYER_PATTERN == 'GRBG':
        sum_r = np.sum(img[0::2, 1::2])
        sum_b = np.sum(img[1::2, 0::2])
        sum_g = np.sum(img[0::2, 0::2]) + np.sum(img[1::2, 1::2])
    elif BAYER_PATTERN == 'BGGR':
        sum_r = np.sum(img[1::2, 1::2])
        sum_b = np.sum(img[0::2, 0::2])
        sum_g = np.sum(img[0::2, 1::2]) + np.sum(img[1::2, 0::2])
    else:
        return 1.0, 1.0

    scale_r = max(1.0, (sum_g / 2.0) / (sum_r + eps))
    scale_b = max(1.0, (sum_g / 2.0) / (sum_b + eps))
    
    return scale_r, scale_b

def parse_srt(srt_path):
    # 这里应放你之前的 SRT 解析代码
    return [] 

# --- 主逻辑 ---
scenes = natsort.natsorted(os.listdir(UNPACK_RAW))

for scene in scenes:
    raw_scene_dir = os.path.join(UNPACK_RAW, scene)
    if not os.path.isdir(raw_scene_dir): continue

    # 提取文件夹中的 Gain 参数
    def extract_val(pattern, string, default=1.0):
        match = re.search(pattern, string, re.IGNORECASE)
        if match:
            val_str = match.group(1).replace('p', '.')
            try: return float(val_str)
            except: return default
        return default

    f_again = extract_val(r"again([\dp\.]+)x", scene, 1.0)
    f_dgain = extract_val(r"dgain([\dp\.]+)x", scene, 1.0)
    # f_ispd = extract_val(r"ispdgain([\dp\.]+)x", scene, 1.0)
    f_ispd = 1.0
    f_drc = extract_val(r"drcgain([\dp\.]+)x", scene, 1.0)
    f_lux = extract_val(r"lux([\dp\.]+)", scene, 1.0)
    f_rgain = extract_val(r"wbr([\dp\.]+)", scene, 1.0)
    f_bgain = extract_val(r"wbb([\dp\.]+)", scene, 1.0)
    f_shutter = extract_val(r"shutter([\dp\.]+)ms", scene, 1.0)

    # 匹配对应的 SRT
    recv_scene_name = re.sub(r"^\d+__", "", scene)
    recv_scene_dir = os.path.join(RECEIVED, recv_scene_name)
    raw_files = natsort.natsorted(glob.glob(os.path.join(raw_scene_dir, "*.raw")))
    if not raw_files: continue

    srt_files = glob.glob(os.path.join(recv_scene_dir, "*.SRT"))
    frames_meta = parse_srt(srt_files[0]) if srt_files else []

    out_scene_path = os.path.join(YAML_ROOT, scene)
    os.makedirs(out_scene_path, exist_ok=True)

    for i, file_path in enumerate(raw_files):
        # 1. 图像处理流程
        if DO_QUAD_PROCESS:
            # 执行下采样
            proc_img = quad_bayer_to_raw(file_path)
        else:
            # 普通读取
            proc_img = np.fromfile(file_path, dtype=np.uint16).reshape([HEIGHT, WIDTH])

        # 2. 计算 AWB (每一帧动态计算，或取第一帧)
        r_gain_calc, b_gain_calc = calculate_awb_gain(proc_img)

        # 3. 准备 YAML 参数
        meta = frames_meta[i] if i < len(frames_meta) else {}
        # gain = f_again * f_dgain
        gain = f_again
        shutter = f_shutter
        iso = gain * 100.0
        expotime = int(1000000 * shutter)
        
        # 优先使用计算出的 AWB，SRT 作为参考
        r_gain = f_rgain
        b_gain = f_bgain
        # cct = int(meta.get("cct", 4000))
        # lux_index = int(meta.get("lux_index", 300))
        cct = 4000
        lux_index = f_lux

        # 4. 写入文件
        yaml_path = os.path.join(out_scene_path, f"{str(i).zfill(3)}.yaml")
        with open(yaml_path, "w") as fo:
            fo.write(EXAMPLE_META)
            fo.write(f"gain: {gain:.4f}\n")
            fo.write(f"SensorAGain: {gain:.4f}\n")
            fo.write(f"sensorgain: {gain:.4f}\n")
            fo.write(f"SensorDGain: 1.00\n")
            fo.write(f"iso: {int(iso)}\n")
            fo.write(f"expotime: {expotime}\n")
            fo.write(f"isp_gain: {f_ispd:.4f}\n")
            fo.write(f"cct: {cct}\n")
            fo.write(f"r_gain: {r_gain:.4f}\n")
            fo.write(f"b_gain: {b_gain:.4f}\n")
            fo.write(f"drc_gain: {f_drc:.4f}\n")
            fo.write(f"lux_index: {lux_index}\n")
            fo.write(f"luxid: {lux_index}\n")

    print(f"[OK] {scene} - Pattern: {BAYER_PATTERN}, Frames: {len(raw_files)}")