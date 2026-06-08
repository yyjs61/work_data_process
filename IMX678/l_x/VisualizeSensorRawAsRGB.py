import cv2, yaml, glob, os, numpy as np
import sys
# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()
ROOT = r"D:\Data\2026_05\20\Test_data_260520\IMX678_Test_data_260520/"

UNPACK_RAW = ROOT + 'unpack_raw/'
YAML_DATA = ROOT + 'yamls_eachFrame/'

BAYER_PATTERN = 'RGGB'
WP = 4095
BP = 200
H = 2160   
W = 3840


OUTPUT_DIR = 'jpg'
OUTPUT_TYPE = 'jpg'

# PSEUDO_ISP_GAIN = 1
# AWB_R_GAIN = 2.0
# AWB_B_GAIN = 1.8

# GAMMA = 3.8
GAMMA = 2.4


DEMOSAIC_DICT = {
    'RGGB': cv2.COLOR_BAYER_BG2BGR_EA,
    'GRBG': cv2.COLOR_BAYER_GB2BGR_EA,
    'GBRG': cv2.COLOR_BAYER_GR2BGR_EA,
    'BGGR': cv2.COLOR_BAYER_RG2BGR_EA
}

def img_ccm(img, ccm):
    ccm = np.array(ccm, dtype=img.dtype)
    img_ccm = np.zeros([H, W, 3],dtype=img.dtype)
    img_ccm = np.matmul(img, ccm.T)
    return img_ccm


# scenes = sorted(os.listdir(UNPACK_RAW))
# for scene in scenes:

scene = sys.argv[1]
os.makedirs(os.path.join(os.path.join(ROOT, OUTPUT_DIR), scene, ), exist_ok=True)
yaml_file = sorted(glob.glob(os.path.join(YAML_DATA, scene,  '*.yaml')))
for id, file in enumerate(sorted(glob.glob(os.path.join(UNPACK_RAW, scene,'*.raw')))):
    try:
        img = np.fromfile(file, dtype='uint16').reshape([H, W]).astype('float')
        img = (img - BP) / (WP - BP)
        img = (img.clip(0, 1) * 65535).astype('uint16')  # Here 65535 is for demosaic, not related to raw image bit depth
        img = cv2.demosaicing(img, DEMOSAIC_DICT[BAYER_PATTERN]).astype('float') / 65535
        yaml_path = yaml_file[id]  
        with open(yaml_path,'r',encoding='utf-8') as file_yaml:
            yaml_content = yaml.safe_load(file_yaml)
        awb_b_gain = yaml_content['b_gain']
        awb_r_gain = yaml_content['r_gain']
        pseudo_isp_gain = yaml_content['isp_gain']
        img[..., 0] *= awb_b_gain
        img[..., 2] *= awb_r_gain
        img *= pseudo_isp_gain
        # img *= 8
        img = img.clip(0,1) ** (1 / GAMMA)
        img = (img.clip(0, 1) * 255).astype('uint8')
        cv2.imwrite(os.path.join(ROOT, OUTPUT_DIR, scene,  os.path.basename(file).replace('.raw', f'.{OUTPUT_TYPE}')), img)
    except:
        print(file)




