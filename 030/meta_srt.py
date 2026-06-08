import os
import glob
import re
import numpy as np
import natsort

# --- 配置参数 ---
# ROOT = "/data/030_Test_20260428"
ROOT = r"D:\Data\2026_06\04\2x_4k60"
RECEIVED = os.path.join(ROOT, "received")
UNPACK_RAW = os.path.join(ROOT, "unpack_raw")
YAML_ROOT = os.path.join(ROOT, "yamls_eachFrame")

os.makedirs(YAML_ROOT, exist_ok=True)

# RAW 图像处理相关常量 (根据实际传感器调整)
BLACK_LEVEL = 64.0
# WHITE_LEVEL = 16383.0
WHITE_LEVEL = 1023.0

BAYER_PATTERN = 'BGGR' 
HEIGHT = 2304
WIDTH = 4096
H = HEIGHT
W = WIDTH
BP = 64.0
WP = 1023

EXAMPLE_META = '''
Black_level: 64.0
White_level: 1023.0
bayer_pattern: BGGR
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]

'''

def get_awb_gain_from_raw2(raw_file_path):
    """
    从raw文件中通过灰度世界算法计算AWB增益 (作为SRT缺失时的补充)
    """
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
        # ... 其他 pattern 逻辑类似
        
        scale_r = max(1.0, sum_g / 2 / sum_r) if sum_r > 0 else 1.0
        scale_b = max(1.0, sum_g / 2 / sum_b) if sum_b > 0 else 1.0
        return scale_r, scale_b
    except Exception as e:
        print(f"  [ERROR] Failed to calculate AWB from RAW: {e}")
        return 1.0, 1.0

def get_awb_gain(file):
    img = file.astype(float)
    img = (img - BP) / (WP - BP)
    img = img.clip(0, 1)
    if BAYER_PATTERN == 'RGGB':
        sum_r = np.sum(img[0::2,0::2])
        sum_b = np.sum(img[1::2,1::2])
        sum_g = np.sum(img[0::2,1::2]) + np.sum(img[1::2,0::2])

        scale_r = max(1, sum_g/2/sum_r) 
        scale_b = max(1, sum_g/2/sum_b)

    elif BAYER_PATTERN == 'GBRG':
        sum_r = np.sum(img[1::2,0::2])
        sum_b = np.sum(img[0::2,1::2])
        sum_g = np.sum(img[0::2,0::2]) + np.sum(img[1::2,1::2])

        scale_r = max(1, sum_g/2/sum_r)
        scale_b = max(1, sum_g/2/sum_b)      

    elif BAYER_PATTERN == 'GRBG':
        sum_r = np.sum(img[0::2,1::2])
        sum_b = np.sum(img[1::2,0::2])
        sum_g = np.sum(img[0::2,0::2]) + np.sum(img[1::2,1::2])

        scale_r = max(1, sum_g/2/sum_r)
        scale_b = max(1, sum_g/2/sum_b)


    elif BAYER_PATTERN == 'BGGR':
        sum_r = np.sum(img[1::2,1::2])
        sum_b = np.sum(img[0::2,0::2])
        sum_g = np.sum(img[0::2,1::2]) + np.sum(img[1::2,0::2])

        scale_r = max(1, sum_g/2/sum_r)
        scale_b = max(1, sum_g/2/sum_b)
    # print(scale_r, scale_b)
    return scale_r, scale_b

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



def parse_font_line(text: str) -> dict:
    meta = {}
    # ISO
    m = re.search(r"\[iso:\s*([\d\.]+)\]", text)
    if m: meta["iso"] = float(m.group(1))

    # Shutter
    m = re.search(r"\[shutter:\s*([\d\.\/]+)\]", text)
    if m:
        s = m.group(1)
        if "/" in s:
            a, b = s.split("/")
            meta["expotime_s"] = float(a)/float(b)
        else:
            meta["expotime_s"] = float(s)

    # RGBGain
    m = re.search(r"\[RGBGain:\s*\(([^)]+)\)\]", text)
    if m:
        parts = m.group(1).split(",")
        if len(parts) == 3:
            r, g, b = [float(x) for x in parts]
            meta["r_gain"] = r / g if g != 0 else 1.0
            meta["b_gain"] = b / g if g != 0 else 1.0

    # 其他参数解析...
    for key, pattern in [("cct", r"\[ct:\s*([\d\.]+)\]"), 
                         ("lux_index", r"\[lux_idx:\s*([\d\.]+)\]"),
                         ("drc_gain", r"\[adrc gain \(([\d\.]+)\)\]")]:
        m = re.search(pattern, text)
        if m: meta[key] = float(m.group(1))
    
    if "lux_index" in meta: meta["luxid"] = meta["lux_index"]
    return meta

def parse_srt(srt_path):
    frames = []
    if not os.path.exists(srt_path): return frames
    with open(srt_path, "r", encoding="utf-8") as f:
        buffer = []
        in_font = False
        for line in f:
            line = line.strip()
            if line.startswith("<font"):
                in_font = True
                buffer = [line]
                continue
            if in_font:
                buffer.append(line)
                if line.endswith("</font>"):
                    text = " ".join(buffer)
                    meta = parse_font_line(text)
                    if meta: frames.append(meta)
                    in_font = False
                    buffer = []
    return frames

# --- 主循环 ---
scenes = natsort.natsorted(os.listdir(UNPACK_RAW))

for scene in scenes:
    raw_scene_dir = os.path.join(UNPACK_RAW, scene)
    if not os.path.isdir(raw_scene_dir): continue

    # 匹配 received 目录
    recv_scene_name = re.sub(r"^\d+__", "", scene)
    recv_scene_dir = os.path.join(RECEIVED, recv_scene_name)

    # 获取 RAW 文件列表
    raw_files = natsort.natsorted(glob.glob(os.path.join(raw_scene_dir, "*.raw")))
    if not raw_files:
        print(f"[SKIP] {scene} (no Raw files)")
        continue

    # 获取 SRT 元数据
    srt_files = glob.glob(os.path.join(recv_scene_dir, "*.SRT"))
    frames_meta = parse_srt(srt_files[0]) if srt_files else []

    out_scene_path = os.path.join(YAML_ROOT, scene)
    os.makedirs(out_scene_path, exist_ok=True)

    # 如果 SRT 帧数少于 RAW，或者根本没有 SRT，我们至少为第一帧计算一个 RAW AWB
    # raw_awb_r, raw_awb_b = get_awb_gain_from_raw(raw_files[0])
    raw_awb_r, raw_awb_b = get_awb_gain(quad_bayer_to_raw(raw_files[0]))
    print(f"r_g : {raw_awb_r} | b_g : {raw_awb_b}")

    frame_cnt = len(raw_files)
    for i in range(frame_cnt):
        # 尝试获取当前帧的 SRT 元数据
        meta = frames_meta[i] if i < len(frames_meta) else {}
        
        yaml_path = os.path.join(out_scene_path, f"{str(i).zfill(3)}.yaml")

        # 基础参数处理
        iso = meta.get("iso", 100)
        # iso = np.clip(iso, 100, 1600)
        gain = iso / 100.0
        expotime = int(meta.get("expotime_s", 0.01) * 1e6)
        
        # AWB Gain 逻辑：优先用 SRT，没有就用 RAW 计算的值
        r_gain = meta.get("r_gain", raw_awb_r)
        b_gain = meta.get("b_gain", raw_awb_b)
        
        cct = int(meta.get("cct", 4000))
        lux_index = int(meta.get("lux_index", 300))
        drc_gain = meta.get("drc_gain", 1.0)
        isp_gain = gain * 7.87 

        with open(yaml_path, "w") as fo:
            fo.write(EXAMPLE_META)
            fo.write(f"gain: {gain:.2f}\n")
            fo.write(f"SensorAGain: {gain:.2f}\n")
            fo.write(f"sensorgain: {gain:.2f}\n")
            fo.write(f"SensorDGain: 1.00\n")
            fo.write(f"iso: {int(iso)}\n")
            fo.write(f"expotime: {expotime}\n")
            fo.write(f"isp_gain: 1.0\n")
            fo.write(f"cct: {cct}\n")
            fo.write(f"r_gain: {r_gain:.4f}\n")
            fo.write(f"b_gain: {b_gain:.4f}\n")
            fo.write(f"drc_gain: {drc_gain:.2f}\n")
            fo.write(f"lux_index: {lux_index}\n")
            fo.write(f"luxid: {lux_index}\n")

    print(f"[OK] {scene}: {frame_cnt} yaml(s) generated (AWB source: {'SRT' if frames_meta else 'RAW Calc'})")

print("\nAll tasks completed.")