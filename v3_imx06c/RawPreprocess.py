import glob, os, natsort, numpy as np
import shutil
# ROOT_PATH = './ROOT_PATH.txt'

# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

ROOT = r"D:\Data\2026_05\06\0429unpack/"
RECEIVED = ROOT + 'received/'
UNPACK_RAW = ROOT + 'unpack_raw/'
N_IMGS_PER_FILE = 1
# N_IMGS_PER_FILE = 100

H = 3072
W = 4096   # 3840


scenes = natsort.natsorted(os.listdir(RECEIVED))
for id, scene in enumerate(scenes): 
    dcg_files = natsort.natsorted(glob.glob(os.path.join(RECEIVED, scene, '*.raw')))
    dst = os.path.join(UNPACK_RAW, str(id ).zfill(2) + '__' + scene )
    os.makedirs(dst, exist_ok=True)

    for i, file in enumerate(dcg_files):

        img = np.fromfile(file, dtype='uint16')
        img_path = os.path.join(dst, f'{str(i).zfill(3)}.raw')
        (img).tofile(img_path)

        # imgs = np.fromfile(file, dtype='uint16').reshape([N_IMGS_PER_FILE, H, W])
        # for j, img in enumerate(imgs[5:95]):
        # for j, img in enumerate(imgs[:]):
            # img_path = os.path.join(dst, f'{str(j).zfill(3)}__long.raw')
            # img_path = os.path.join(dst, f'{str(j).zfill(3)}.raw')
            # img_path = os.path.join(dst, f'{str(j * 2).zfill(3)}__long.raw')
            # (img>>2).tofile(img_path)


    
