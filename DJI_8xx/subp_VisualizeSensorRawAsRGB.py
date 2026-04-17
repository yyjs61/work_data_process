import cv2, yaml, glob, os, sys, numpy as np


# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()
# ROOT = '/home/user/afs_data/LeeSin_Xie/quadraw_for_yw_20260408/'
# ROOT = '/home/user/afs_data/LeeSin_Xie/data/TestData/'
ROOT = r"D:\Data\20260416\quad_potraitraw_for_yw-2026-04-16\quad_potraitraw_for_yw/"


UNPACK_RAW = ROOT + 'unpack_raw/'
YAML_DATA = ROOT + 'yamls_eachFrame/'


# H = 2304
# W = 4096

H = 2304
W = 4096

# H = 2256
# W = 4000

# H = 3056
# W = 2720
# height: 2160.0
# width: 3840.0
# H = 2160
# W = 3840
BAYER_PATTERN = 'BGGR'
# BAYER_PATTERN = 'RGGB'


# 14bit
# WP = 16383
# BP = 1024

# 10bit
# WP = 1023
# BP = 64

# 12bit
WP = 4095
# BP = 256
BP = 64

OUTPUT_DIR = 'jpg'
OUTPUT_TYPE = 'jpg'

# PSEUDO_ISP_GAIN = 1
# AWB_R_GAIN = 2.0
# AWB_B_GAIN = 1.8
GAMMA = 2.8


DEMOSAIC_DICT = {
    'RGGB': cv2.COLOR_BAYER_BG2BGR_EA,
    'GRBG': cv2.COLOR_BAYER_GB2BGR_EA,
    'GBRG': cv2.COLOR_BAYER_GR2BGR_EA,
    'BGGR': cv2.COLOR_BAYER_RG2BGR_EA
}


def HEX2CHW(quad_bayer):
    assert len(quad_bayer.shape) == 2
    H, W = quad_bayer.shape[0], quad_bayer.shape[1]
    chw = np.zeros([4, H//2, W//2], dtype=quad_bayer.dtype)
    SHIFT = {    0: {'Y': 0, 'X': 0},    1: {'Y': 0, 'X': 4},    2: {'Y': 4, 'X': 0},    3: {'Y': 4, 'X': 4},   }
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
    SHIFT = {    0: {'Y': 0, 'X': 0},    1: {'Y': 0, 'X': 2},    2: {'Y': 2, 'X': 0},    3: {'Y': 2, 'X': 2},   }
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


# scenes = sorted(os.listdir(UNPACK_RAW))
# for scene in scenes:
scene = sys.argv[1]
os.makedirs(os.path.join(os.path.join(ROOT, OUTPUT_DIR), scene), exist_ok=True)
for index, file in enumerate(sorted(glob.glob(os.path.join(UNPACK_RAW, scene, '*.raw')))):
    img = np.fromfile(file, dtype='uint16').reshape([H, W]).astype('float')

    # quad
    img = QuadBayer2CHW(img)
    # img = HEX2CHW(img)    #hex
    img = CHW2RGB(img)

    img = (img - BP) / (WP - BP)
    img = img.clip(0, 1)
    # img = awb(img)

    # normal版本的
    # img = (img.clip(0, 1) * 65535).astype('uint16')  # Here 65535 is for demosaic, not related to raw image bit depth
    # img = cv2.demosaicing(img, DEMOSAIC_DICT[BAYER_PATTERN]).astype('float') / 65535

    yaml_path = os.path.join(YAML_DATA,scene,str(index).zfill(3) + '.yaml')  
    with open(yaml_path,'r',encoding='utf-8') as file_yaml:
        yaml_content = yaml.safe_load(file_yaml)
    awb_b_gain = yaml_content['b_gain']
    awb_r_gain = yaml_content['r_gain']
    img[..., 0] *= awb_b_gain
    img[..., 2] *= awb_r_gain
    img *= yaml_content['isp_gain']
    img = img ** (1 / GAMMA)
    img = (img.clip(0, 1) * 255).astype('uint8')

    # ===== Gray World AWB (inline) =====
    # eps = 1e-6
    # mean_r = img[..., 2].mean()
    # mean_g = img[..., 1].mean()
    # mean_b = img[..., 0].mean()

    # gray = (mean_r + mean_g + mean_b) / 3.0

    # gain_r = gray / (mean_r + eps)
    # gain_g = gray / (mean_g + eps)
    # gain_b = gray / (mean_b + eps)

    # img[..., 2] *= gain_r
    # img[..., 1] *= gain_g
    # img[..., 0] *= gain_b

    # img = img ** (1 / GAMMA)
    # img = (img.clip(0, 1) * 255).astype('uint8')
    cv2.imwrite(os.path.join(ROOT, OUTPUT_DIR, scene, os.path.basename(file).replace('.raw', f'.{OUTPUT_TYPE}')), img)



