import os, glob, natsort, shutil, numpy as np

# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

# ROOT = '/data/OVH9000_DCG_20260326_portrait/'
ROOT = r'D:\Data\20260415\honor\OVH9000_DCG_20260415_lab\honor'

RECEIVED = ROOT + 'received/'
UNPACK_RAW = ROOT + 'unpack_raw/'
OUTPUT_RAW = ROOT + 'output_raw/'

scenes = natsort.natsorted(os.listdir(RECEIVED))
for id, scene in enumerate(scenes):
    dir = os.path.join(UNPACK_RAW, str(id).zfill(2) + '__' + scene)
    os.makedirs(dir, exist_ok=True)
    imgs = natsort.natsorted(glob.glob(os.path.join(RECEIVED, scene, '*in_4096*.raw')))
    for i, img in enumerate(imgs):      
        shutil.copy(img, os.path.join(dir, str(i).zfill(3) + '_' + os.path.basename(img)))

    # dir = os.path.join(OUTPUT_RAW, str(id).zfill(2) + '__' + scene)
    # os.makedirs(dir, exist_ok=True)
    # imgs = natsort.natsorted(glob.glob(os.path.join(RECEIVED, scene, '*out_4096*.raw')))
    # for i, img in enumerate(imgs):      
    #     shutil.move(img, os.path.join(dir, str(i).zfill(3) + '_' + os.path.basename(img)))
