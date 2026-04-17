import cv2, yaml, glob, os, sys, numpy as np

# ==================== 配置区域 ====================
# ROOT_PATH = './ROOT_PATH.txt'
# try:
#     with open(ROOT_PATH, 'r') as file:
#         ROOT = file.readline().strip()
# except:
ROOT = r'C:\Users\admin.DESKTOP-QNCO006\Desktop\Data\OV50X\OV50X_DCGandLOFIC_20260410__lab_ipad/'

UNPACK_RAW = os.path.join(ROOT, 'unpack_raw')
YAML_DATA = os.path.join(ROOT, 'yamls_eachFrame')
H = 3072
W = 4096
BAYER_PATTERN = 'BGGR'

# 移除硬编码的 WP 和 BP，改为从 YAML 动态读取
# WP = 1023
# BP = 64

OUTPUT_DIR = 'jpg'
OUTPUT_TYPE = 'jpg'
PSEUDO_ISP_GAIN = 1
AWB_R_GAIN = 2.0
AWB_B_GAIN = 1.8
GAMMA = 2.4

DEMOSAIC_DICT = {
    'RGGB': cv2.COLOR_BAYER_BG2BGR_EA,
    'GRBG': cv2.COLOR_BAYER_GB2BGR_EA,
    'GBRG': cv2.COLOR_BAYER_GR2BGR_EA,
    'BGGR': cv2.COLOR_BAYER_RG2BGR_EA
}
# ==================== 配置区域结束 ====================

def HEX2CHW(quad_bayer):
    assert len(quad_bayer.shape) == 2
    H, W = quad_bayer.shape[0], quad_bayer.shape[1]
    chw = np.zeros([4, H//2, W//2], dtype=quad_bayer.dtype)
    SHIFT = {
        0: {'Y': 0, 'X': 0},
        1: {'Y': 0, 'X': 4},
        2: {'Y': 4, 'X': 0},
        3: {'Y': 4, 'X': 4},
    }
    for i, c in enumerate(chw):
        c[0::4, 0::4] = quad_bayer[SHIFT[i]['Y'] + 0::8, SHIFT[i]['X'] + 0::8]
        c[0::4, 1::4] = quad_bayer[SHIFT[i]['Y'] + 0::8, SHIFT[i]['X'] + 1::8]
        c[0::4, 2::4] = quad_bayer[SHIFT[i]['Y'] + 0::8, SHIFT[i]['X'] + 2::8]
        c[0::4, 3::4] = quad_bayer[SHIFT[i]['Y'] + 0::8, SHIFT[i]['X'] + 3::8]

        c[1::4, 0::4] = quad_bayer[SHIFT[i]['Y'] + 1::8, SHIFT[i]['X'] + 0::8]
        c[1::4, 1::4] = quad_bayer[SHIFT[i]['Y'] + 1::8, SHIFT[i]['X'] + 1::8]
        c[1::4, 2::4] = quad_bayer[SHIFT[i]['Y'] + 1::8, SHIFT[i]['X'] + 2::8]
        c[1::4, 3::4] = quad_bayer[SHIFT[i]['Y'] + 1::8, SHIFT[i]['X'] + 3::8]

        c[2::4, 0::4] = quad_bayer[SHIFT[i]['Y'] + 2::8, SHIFT[i]['X'] + 0::8]
        c[2::4, 1::4] = quad_bayer[SHIFT[i]['Y'] + 2::8, SHIFT[i]['X'] + 1::8]
        c[2::4, 2::4] = quad_bayer[SHIFT[i]['Y'] + 2::8, SHIFT[i]['X'] + 2::8]
        c[2::4, 3::4] = quad_bayer[SHIFT[i]['Y'] + 2::8, SHIFT[i]['X'] + 3::8]

        c[3::4, 0::4] = quad_bayer[SHIFT[i]['Y'] + 3::8, SHIFT[i]['X'] + 0::8]
        c[3::4, 1::4] = quad_bayer[SHIFT[i]['Y'] + 3::8, SHIFT[i]['X'] + 1::8]
        c[3::4, 2::4] = quad_bayer[SHIFT[i]['Y'] + 3::8, SHIFT[i]['X'] + 2::8]
        c[3::4, 3::4] = quad_bayer[SHIFT[i]['Y'] + 3::8, SHIFT[i]['X'] + 3::8]

    return chw

def QuadBayer2CHW(quad_bayer):
    assert len(quad_bayer.shape) == 2
    H, W = quad_bayer.shape[0], quad_bayer.shape[1]
    chw = np.zeros([4, H//2, W//2], dtype=quad_bayer.dtype)
    SHIFT = {
        0: {'Y': 0, 'X': 0},
        1: {'Y': 0, 'X': 2},
        2: {'Y': 2, 'X': 0},
        3: {'Y': 2, 'X': 2},
    }
    for i, c in enumerate(chw):
        c[0::2, 0::2] = quad_bayer[SHIFT[i]['Y'] + 0::4, SHIFT[i]['X'] + 0::4]
        c[0::2, 1::2] = quad_bayer[SHIFT[i]['Y'] + 0::4, SHIFT[i]['X'] + 1::4]
        c[1::2, 0::2] = quad_bayer[SHIFT[i]['Y'] + 1::4, SHIFT[i]['X'] + 0::4]
        c[1::2, 1::2] = quad_bayer[SHIFT[i]['Y'] + 1::4, SHIFT[i]['X'] + 1::4]
    return chw

def CHW2RGB(CHW):
    if BAYER_PATTERN == 'RGGB':
        r, g0, g1, b = CHW
        g = (g0 + g1) / 2.0
        return np.stack([b, g, r], axis=-1)

# ==================== 主处理流程 ====================
scenes = sorted(os.listdir(UNPACK_RAW))

# 支持命令行参数指定场景
if len(sys.argv) > 1:
    scenes = [sys.argv[1]]
    print(f"[Info] 仅处理指定场景：{scenes[0]}")
else:
    print(f"[Info] 处理所有场景，共 {len(scenes)} 个")

for scene in scenes:
    scene_output_dir = os.path.join(ROOT, OUTPUT_DIR, scene)
    os.makedirs(scene_output_dir, exist_ok=True)
    
    raw_files = sorted(glob.glob(os.path.join(UNPACK_RAW, scene, '*.raw')))
    print(f"\n{'='*60}")
    print(f"处理场景：{scene}")
    print(f"文件数量：{len(raw_files)}")
    print(f"{'='*60}")
    
    for index, file in enumerate(raw_files):
        # 1. 读取 RAW 数据
        img = np.fromfile(file, dtype='uint16').reshape([H, W]).astype('float')
        
        # 如果是 quad bayer 则解注释下面两行
        # img = QuadBayer2CHW(img)
        # img = CHW2RGB(img)
        
        # 2. 读取对应的 YAML 文件
        yaml_path = os.path.join(YAML_DATA, scene, str(index).zfill(3) + '.yaml')
        
        # 3. 根据奇偶性判断暗帧/亮帧，并设置 BP 和 WP
        if os.path.exists(yaml_path):
            with open(yaml_path, 'r', encoding='utf-8') as file_yaml:
                yaml_content = yaml.safe_load(file_yaml)
            
            # 判断奇偶性：偶数=暗帧，奇数=亮帧
            if index % 2 == 0:
                # 暗帧：使用 under_Black_level 和 under_White_level
                BP = yaml_content.get('under_Black_level', 256)
                WP = yaml_content.get('under_White_level', 4096)
                frame_type = "暗帧"
            else:
                # 亮帧：使用 Black_level 和 White_level
                BP = yaml_content.get('Black_level', 256)
                WP = yaml_content.get('White_level', 16383)
                frame_type = "亮帧"
            
            print(f"  [{frame_type}] Frame {str(index).zfill(3)}: BP={BP}, WP={WP}")
        else:
            # YAML 文件不存在，使用默认值
            BP = 64
            WP = 1023
            print(f"  [警告] YAML 文件不存在，使用默认值：BP={BP}, WP={WP}")
        
        # 4. 归一化处理 (使用动态获取的 BP 和 WP)
        img = (img - BP) / (WP - BP)
        img = img.clip(0, 1)
        
        # 5. Bayer 转 RGB
        # 下面两行是 bayer 的
        img = (img.clip(0, 1) * 65535).astype('uint16')  # Here 65535 is for demosaic, not related to raw image bit depth
        img = cv2.demosaicing(img, DEMOSAIC_DICT[BAYER_PATTERN]).astype('float') / 65535
        
        # 6. 应用白平衡增益
        if os.path.exists(yaml_path):
            with open(yaml_path, 'r', encoding='utf-8') as file_yaml:
                yaml_content = yaml.safe_load(file_yaml)
            awb_b_gain = yaml_content.get('b_gain', 1.8)
            awb_r_gain = yaml_content.get('r_gain', 2.0)
            img[..., 0] *= awb_b_gain
            img[..., 2] *= awb_r_gain
            img *= yaml_content.get('isp_gain', 1.0)
        
        # 7. Gamma 校正并保存
        img = img ** (1 / GAMMA)
        img = (img.clip(0, 1) * 255).astype('uint8')
        
        output_path = os.path.join(scene_output_dir, os.path.basename(file).replace('.raw', f'.{OUTPUT_TYPE}'))
        cv2.imwrite(output_path, img)

print(f"\n{'='*60}")
print("全部场景处理完成")
print(f"{'='*60}")