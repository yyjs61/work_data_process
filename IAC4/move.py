import os, glob, natsort, shutil, numpy as np

# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

# ROOT = r'D:\Data\2026_05\07\imx01f_EVT2p3_0040\sensor_raw_ultrawide/'
# ROOT = r'D:\Data\2026_05\22\IAC4_IMX01F_DCG_ER4_UltralWide_20260522/'
ROOT = r'D:\Data\2026_05\25\IAC4_IMX01F_DCG_ER4_Wide_20260525/'

RECEIVED = ROOT + 'received/'
UNPACK_RAW = ROOT + 'unpack_raw/'
OUTPUT_RAW = ROOT + 'output_raw/'

scenes = natsort.natsorted(os.listdir(RECEIVED))
for id, scene in enumerate(scenes):
    dir = os.path.join(UNPACK_RAW, str(id).zfill(2) + '__' + scene)
    os.makedirs(dir, exist_ok=True)
    imgs = natsort.natsorted(glob.glob(os.path.join(RECEIVED, scene, '*.raw')))
    for i, img in enumerate(imgs):      
        shutil.copy(img, os.path.join(dir, str(i).zfill(3) + '_' + os.path.basename(img)))