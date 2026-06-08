import cv2
import yaml
import glob
import os
import sys
import numpy as np

# --- 配置参数 ---
# ROOT = '/data/V210_OV50X_Lofic_empty_shot_20260603/'
# ROOT = r'D:\Data\2026_06\05\V210_OV50X_Lofic_human_face_20260603/'
ROOT = r'D:\Data\2026_06\05\V210_OV50X_quad_night_20260519/'

UNPACK_RAW = ROOT + 'unpack_raw/'
YAML_DATA = ROOT + 'yamls_eachFrame/'

H = 2240
W = 3968
BAYER_PATTERN = 'BGGR'

OUTPUT_DIR = 'jpg'
OUTPUT_TYPE = 'jpg'
GAMMA = 2.8

DEMOSAIC_DICT = {
    'RGGB': cv2.COLOR_BAYER_BG2BGR_EA,
    'GRBG': cv2.COLOR_BAYER_GB2BGR_EA,
    'GBRG': cv2.COLOR_BAYER_GR2BGR_EA,
    'BGGR': cv2.COLOR_BAYER_RG2BGR_EA
}

# 保留原有函数定义（如果需要处理 QuadBayer 可以取消注释相关调用）
def QuadBayer2CHW(quad_bayer):
    assert len(quad_bayer.shape) == 2
    H, W = quad_bayer.shape[0], quad_bayer.shape[1]
    chw = np.zeros([4, H//2, W//2], dtype=quad_bayer.dtype)
    SHIFT = {0: {'Y': 0, 'X': 0}, 1: {'Y': 0, 'X': 2}, 2: {'Y': 2, 'X': 0}, 3: {'Y': 2, 'X': 2}}
    for i, c in enumerate(chw):
        c[0::2, 0::2] = quad_bayer[SHIFT[i]['Y'] + 0::4, SHIFT[i]['X'] + 0::4]
        c[0::2, 1::2] = quad_bayer[SHIFT[i]['Y'] + 0::4, SHIFT[i]['X'] + 1::4]
        c[1::2, 0::2] = quad_bayer[SHIFT[i]['Y'] + 1::4, SHIFT[i]['X'] + 0::4]
        c[1::2, 1::2] = quad_bayer[SHIFT[i]['Y'] + 1::4, SHIFT[i]['X'] + 1::4]
    return chw

def CHW2RGB(CHW):
    if BAYER_PATTERN == 'RGGB':
        r, g0, g1, b = CHW
        g = (g0 + g1)/2.0
        return np.stack([b, g, r], axis=-1)
    if BAYER_PATTERN == 'GRBG':
        g0, r, b, g1 = CHW
        g = (g0 + g1)/2.0
        return np.stack([b, g, r], axis=-1)
    if BAYER_PATTERN == 'BGGR':
        b, g0, g1, r = CHW
        g = (g0 + g1)/2.0
        return np.stack([b, g, r], axis=-1)

# --- 主处理逻辑 ---
if len(sys.argv) < 2:
    print("Usage: python script.py <scene_name>")
    sys.exit(1)

scene = sys.argv[1]
os.makedirs(os.path.join(ROOT, OUTPUT_DIR, scene), exist_ok=True)

# 获取所有 raw 文件并排序
raw_files = sorted(glob.glob(os.path.join(UNPACK_RAW, scene, '*.raw')))

for index, file in enumerate(raw_files):
    # 读取 raw 数据
    img = np.fromfile(file, dtype='uint16').reshape([H, W]).astype('float')
    
    # 读取对应的 yaml 元数据
    yaml_path = os.path.join(YAML_DATA, scene, str(index).zfill(3) + '.yaml')  
    with open(yaml_path, 'r', encoding='utf-8') as file_yaml:
        yaml_content = yaml.safe_load(file_yaml)
        
    # ==========================================
    # 区分 DCG 帧 和 LOFIC 帧
    # 假设: 偶数索引 (0, 2, 4...) 为 DCG 帧，奇数索引 (1, 3, 5...) 为 LOFIC 帧
    # 如果你的数据集中奇数是 DCG，偶数是 LOFIC，请将下面的 index % 2 == 0 改为 index % 2 != 0
    # ==========================================
    is_dcg = (index % 2 != 0)
    
    if is_dcg:
        bp = float(yaml_content['Black_level'])
        wp = float(yaml_content['White_level'])
        sensor_gain = float(yaml_content['SensorAGain']) * float(yaml_content['SensorDGain'])
        suffix = '_dcg'
    else:
        bp = float(yaml_content['under_Black_level'])
        wp = float(yaml_content['under_White_level'])
        sensor_gain = float(yaml_content['under_SensorAGain']) * float(yaml_content['under_SensorDGain'])
        suffix = '_lofic'
        
    awb_b_gain = float(yaml_content['b_gain'])
    awb_r_gain = float(yaml_content['r_gain'])
    isp_gain = float(yaml_content['isp_gain'])

    # 1. 归一化 (使用各自帧的 BP 和 WP)
    img = (img - bp) / (wp - bp)
    img = img.clip(0, 1)
    
    # 2. Demosaic
    # 乘以 65535 是为了满足 cv2.demosaicing 对 uint16 的输入要求
    img = (img.clip(0, 1) * 65535).astype('uint16')  
    img = cv2.demosaicing(img, DEMOSAIC_DICT[BAYER_PATTERN]).astype('float') / 65535

    # 3. AWB 白平衡
    img[..., 0] *= awb_b_gain  # B 通道
    img[..., 2] *= awb_r_gain  # R 通道
    
    # 4. 应用 Gain (Sensor Gain + ISP Gain)
    img *= sensor_gain
    img *= isp_gain
    
    # 5. Gamma 校正
    img = img ** (1.0 / GAMMA)
    
    # 6. 转换为 8-bit 并保存
    img = (img.clip(0, 1) * 255).astype('uint8')
    
    # 在文件名中添加 _dcg 或 _lofic 后缀以便区分
    out_name = os.path.basename(file).replace('.raw', f'{suffix}.{OUTPUT_TYPE}')
    out_path = os.path.join(ROOT, OUTPUT_DIR, scene, out_name)
    cv2.imwrite(out_path, img)
    
    print(f"[{index:03d}] Saved: {out_name} (BP={bp}, WP={wp}, Gain={sensor_gain:.3f})")

print(f"\nScene '{scene}' visualization completed!")