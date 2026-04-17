import cv2, yaml, glob, os, sys, numpy as np


# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()
ROOT = '/data/SC5A0XS_DCGandLOFIC_20260211_inner/'

UNPACK_RAW = ROOT + 'unpack_raw/'
YAML_DATA = ROOT + 'yamls_eachFrame/'

H = 2160
W = 3840

# BAYER_PATTERN = 'RGGB'
BAYER_PATTERN = 'BGGR'

# BAYER_PATTERN = 'GBRG'
# BAYER_PATTERN = 'GRBG'

WP = 16383
BP = 1024


OUTPUT_DIR = 'jpg'
OUTPUT_TYPE = 'jpg'

# PSEUDO_ISP_GAIN = 1
# AWB_R_GAIN = 2.0
# AWB_B_GAIN = 1.8
GAMMA = 2.4


DEMOSAIC_DICT = {
    'RGGB': cv2.COLOR_BAYER_BG2BGR_EA,
    'GRBG': cv2.COLOR_BAYER_GB2BGR_EA,
    'GBRG': cv2.COLOR_BAYER_GR2BGR_EA,
    'BGGR': cv2.COLOR_BAYER_RG2BGR_EA
}


def awb(img):
    if BAYER_PATTERN == 'RGGB':
        sum_r = np.sum(img[0::2,0::2])
        sum_b = np.sum(img[1::2,1::2])
        sum_g = np.sum(img[0::2,1::2]) + np.sum(img[1::2,0::2])

        scale_r = max(1, sum_g/2/sum_r) 
        scale_b = max(1, sum_g/2/sum_b)

        img[0::2,0::2] *= scale_r
        img[1::2,1::2] *= scale_b

    elif BAYER_PATTERN == 'GBRG':
        sum_r = np.sum(img[1::2,0::2])
        sum_b = np.sum(img[0::2,1::2])
        sum_g = np.sum(img[0::2,0::2]) + np.sum(img[1::2,1::2])

        scale_r = max(1, sum_g/2/sum_r)
        scale_b = max(1, sum_g/2/sum_b)      

        img[1::2,0::2] *= scale_r
        img[0::2,1::2] *= scale_b
    elif BAYER_PATTERN == 'GRBG':
        sum_r = np.sum(img[0::2,1::2])
        sum_b = np.sum(img[1::2,0::2])
        sum_g = np.sum(img[0::2,0::2]) + np.sum(img[1::2,1::2])

        scale_r = max(1, sum_g/2/sum_r)
        scale_b = max(1, sum_g/2/sum_b)

        img[0::2,1::2] *= scale_r
        img[1::2,0::2] *= scale_b 

    elif BAYER_PATTERN == 'BGGR':
        sum_r = np.sum(img[1::2,1::2])
        sum_b = np.sum(img[0::2,0::2])
        sum_g = np.sum(img[0::2,1::2]) + np.sum(img[1::2,0::2])

        scale_r = max(1, sum_g/2/sum_r)
        scale_b = max(1, sum_g/2/sum_b)
            
        img[1::2,1::2] *= scale_r
        img[0::2,0::2] *= scale_b

    print(scale_r,scale_b)
    return img


# scenes = sorted(os.listdir(UNPACK_RAW))
# for scene in scenes:

scene = sys.argv[1]
os.makedirs(os.path.join(os.path.join(ROOT, OUTPUT_DIR), scene), exist_ok=True)
for index, file in enumerate(sorted(glob.glob(os.path.join(UNPACK_RAW, scene, '*.raw')))):
    img = np.fromfile(file, dtype='uint16').reshape([H, W]).astype('float')

    img = (img - BP) / (WP - BP)
    # img = awb(img)
    img = (img.clip(0, 1) * 65535).astype('uint16')  # Here 65535 is for demosaic, not related to raw image bit depth
    img = cv2.demosaicing(img, DEMOSAIC_DICT[BAYER_PATTERN]).astype('float') / 65535
    yaml_file = os.path.basename(file).split('__')[0] + '.yaml'
    yaml_path = os.path.join(YAML_DATA,scene,yaml_file)  
    with open(yaml_path,'r',encoding='utf-8') as file_yaml:
        yaml_content = yaml.safe_load(file_yaml)
    awb_b_gain = yaml_content['b_gain']
    awb_r_gain = yaml_content['r_gain']
    img[..., 0] *= awb_b_gain
    img[..., 2] *= awb_r_gain
    # img *= yaml_content['isp_gain']
    img = img ** (1 / GAMMA)
    img = (img.clip(0, 1) * 255).astype('uint8')
    cv2.imwrite(os.path.join(ROOT, OUTPUT_DIR, scene, os.path.basename(file).replace('.raw', f'.{OUTPUT_TYPE}')), img)


