import cv2, yaml, glob, os, sys, numpy as np


# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

ROOT = '/data/imx06a/'
UNPACK_RAW = ROOT + 'unpack_raw/'
YAML_DATA = ROOT + 'yamls_eachFrame/'

H = 2160
W = 3840

BAYER_PATTERN = 'RGGB'


# WP = 16383.0
# BP = 1024.0


# WP = 1023.0
# BP = 64.0

WP = 4095.0
BP = 256.0


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
    # img = QuadBayer2CHW(img)
    # img = CHW2RGB(img)
    img = (img - BP) / (WP - BP)
    # img = awb(img)
    img = (img.clip(0, 1) * 65535).astype('uint16')  # Here 65535 is for demosaic, not related to raw image bit depth
    img = cv2.demosaicing(img, DEMOSAIC_DICT[BAYER_PATTERN]).astype('float') / 65535

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
    cv2.imwrite(os.path.join(ROOT, OUTPUT_DIR, scene, os.path.basename(file).replace('.raw', f'.{OUTPUT_TYPE}')), img)


