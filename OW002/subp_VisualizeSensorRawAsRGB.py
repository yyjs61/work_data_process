import cv2, yaml, glob, os, sys, numpy as np


# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

ROOT = '/data/SC590_dcg_20260319_sensorraw/'

UNPACK_RAW = ROOT + 'unpack_raw/'
YAML_DATA = ROOT + 'yamls_eachFrame/'

H = 3072
W = 4096

BAYER_PATTERN = 'RGGB'

WP = 16383.0
BP = 1024.0

OUTPUT_DIR = 'jpg'
OUTPUT_TYPE = 'jpg'

GAMMA = 2.8

DEMOSAIC_DICT = {
    'RGGB': cv2.COLOR_BAYER_BG2BGR_EA,
    'GRBG': cv2.COLOR_BAYER_GB2BGR_EA,
    'GBRG': cv2.COLOR_BAYER_GR2BGR_EA,
    'BGGR': cv2.COLOR_BAYER_RG2BGR_EA
}

# scenes = sorted(os.listdir(UNPACK_RAW))
# for scene in scenes:

scene = sys.argv[1]
os.makedirs(os.path.join(os.path.join(ROOT, OUTPUT_DIR), scene), exist_ok=True)
for index, file in enumerate(sorted(glob.glob(os.path.join(UNPACK_RAW, scene, '*.raw')))):
    img = np.fromfile(file, dtype='uint16').reshape([H, W]).astype('float')
    img = (img - BP) / (WP - BP)
    img = (img.clip(0, 1) * 65535).astype('uint16')  # Here 65535 is for demosaic, not related to raw image bit depth
    img = cv2.demosaicing(img, DEMOSAIC_DICT[BAYER_PATTERN]).astype('float') / 65535

    yaml_path = os.path.join(YAML_DATA,scene,str(index).zfill(3) + '.yaml')  
    with open(yaml_path,'r',encoding='utf-8') as file_yaml:
        yaml_content = yaml.safe_load(file_yaml)
    awb_b_gain = yaml_content['b_gain']
    awb_r_gain = yaml_content['r_gain']
    img[..., 0] *= awb_b_gain
    img[..., 2] *= awb_r_gain
    # img[..., 0] *= 1.8
    # img[..., 2] *= 2.0
    img *= yaml_content['isp_gain']
    img = img ** (1 / GAMMA)
    img = (img.clip(0, 1) * 255).astype('uint8')
    cv2.imwrite(os.path.join(ROOT, OUTPUT_DIR, scene, os.path.basename(file).replace('.raw', f'.{OUTPUT_TYPE}')), img)


