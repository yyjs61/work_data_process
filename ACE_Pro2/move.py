import glob, os, natsort, numpy as np

ROOT = '/data/OVH9000_DCG_20260417_low_light/ace_pro2/'
RECEIVED = ROOT + 'received/'
UNPACK_RAW = ROOT + 'unpack_raw/'
N_IMGS_PER_FILE = 50  # 每个raw文件50帧
H, W = 3072, 4096

scenes = natsort.natsorted(os.listdir(RECEIVED))
global_idx = 0  # 全局计数器

for scene in scenes:
    raw_files = natsort.natsorted(glob.glob(os.path.join(RECEIVED, scene, '*.raw')))
    
    for file in raw_files:
        dst = os.path.join(UNPACK_RAW, f'{str(global_idx).zfill(2)}__{scene}')
        os.makedirs(dst, exist_ok=True)
        
        imgs = np.fromfile(file, dtype='uint16').reshape([N_IMGS_PER_FILE, H, W])
        
        for j, img in enumerate(imgs):
            img_path = os.path.join(dst, f'{str(j).zfill(3)}.raw')
            (img >> 2).tofile(img_path)
        
        global_idx += 1  