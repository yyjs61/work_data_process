import glob, os, natsort, numpy as np
import shutil

# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

ROOT = '/data/SC5A0XS_DCGandLOFIC_20260211_inner/'

RECEIVED = ROOT + 'received/'
UNPACK_RAW = ROOT + 'unpack_raw/'
BLENDING = ROOT + 'blending/'
N_IMGS_PER_FILE = 100
H = 2160
W = 3840   # 3840


scenes = natsort.natsorted(os.listdir(RECEIVED))
for id, scene in enumerate(scenes):
    sub_scenes =[]

    lofic_files = natsort.natsorted(glob.glob(os.path.join(RECEIVED, scene, '*VCNum0*.raw')))
    for i, file in enumerate(lofic_files):
        # dst = os.path.join(UNPACK_RAW, str(i + id ).zfill(2) + '__' + scene )
        dst = os.path.join(UNPACK_RAW, str(i + id * len(sub_scenes)).zfill(2) + '__'+ scene + '__' + sub_scenes[i])
        os.makedirs(dst, exist_ok=True)
        imgs = np.fromfile(file, dtype='uint16').reshape([N_IMGS_PER_FILE, H, W])
        # for j, img in enumerate(imgs[5:95]):
        #     img_path = os.path.join(dst, f'{str(j * 2 + 1).zfill(3)}__short.raw')
        #     (img>>2).tofile(img_path)
        avg_img = np.mean((imgs>>2).astype(np.float16), axis=0).astype(np.uint16)
        blending_dst = os.path.join(BLENDING, scene)
        os.makedirs(blending_dst,exist_ok=True)
        (avg_img).tofile(os.path.join(blending_dst, 'lofic '+ os.path.basename(file)))


    dcg_files = natsort.natsorted(glob.glob(os.path.join(RECEIVED, scene, '*VCNum1*.raw')))
    for i, file in enumerate(dcg_files):
        dst = os.path.join(UNPACK_RAW, str(i + id ).zfill(2) + '__' + scene )
        os.makedirs(dst, exist_ok=True)
        imgs = np.fromfile(file, dtype='uint16').reshape([N_IMGS_PER_FILE, H, W])
        for j, img in enumerate(imgs[5:95]):
            img_path = os.path.join(dst, f'{str(j * 2).zfill(3)}__long.raw')
            (img>>2).tofile(img_path)


    
