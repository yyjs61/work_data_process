import os, glob, natsort, shutil, numpy as np

# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()
ROOT = '/data/20260313_PGC_IMX06A_DCG/'

RECEIVED = ROOT + 'received/'
MIPI_RAW = ROOT + 'unpack_raw/'

scenes = natsort.natsorted(os.listdir(RECEIVED))
for id, scene in enumerate(scenes):
    os.rename(os.path.join(RECEIVED, scene), os.path.join(RECEIVED, scene.replace(' ', '').replace(',', '_').replace('.', 'p')))

scenes = natsort.natsorted(os.listdir(RECEIVED))
for id, scene in enumerate(scenes):
    # dir = os.path.join(MIPI_RAW, str(id).zfill(2) + '__' + scene.replace(' ', '').replace(',', '_').replace('.', 'p'))
    dir = os.path.join(ROOT, 'unpack_raw', str(id).zfill(2) + '__' + scene.replace(' ', '').replace(',', '_').replace('.', 'p'))
    os.makedirs(dir, exist_ok=True)

    # files = natsort.natsorted(glob.glob(os.path.join(RECEIVED, scene, 'Session*', '*.raw')))
    files = natsort.natsorted(glob.glob(os.path.join(RECEIVED, scene, '*.raw')))

    files = natsort.natsorted([i for i in files if os.path.getsize(i) == 16588800])

    for i, file in enumerate(files):     
        # shutil.move(file, os.path.join(dir, str(i).zfill(3) + '_' + os.path.basename(file) + '.raw'))
        shutil.copy(file, os.path.join(dir, str(i).zfill(3) + '_' + os.path.basename(file)))

    # files = natsort.natsorted([i for i in files if os.path.getsize(i) >= 16588800])
    # for i, file in enumerate(files):
    #     raw = np.fromfile(file, dtype = np.uint16)[:3840*2160]
    #     # print(scene, os.path.basename(file), np.sum(raw[3840*2160:]), np.sum(raw))
    #     raw.tofile(os.path.join(dir, str(i).zfill(3) + '_' + os.path.basename(file)))      
