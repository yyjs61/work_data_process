import os, glob, natsort, shutil, numpy as np

# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

ROOT = '/data/0313-1/'
RECEIVED = ROOT + 'received/'
UNPACK_RAW = ROOT + 'unpack_raw/'


scenes = natsort.natsorted(os.listdir(RECEIVED))
for id, scene in enumerate(scenes):
    os.rename(os.path.join(RECEIVED, scene), os.path.join(RECEIVED, scene.replace(' ', '').replace(',', '_').replace('.', 'p')))


scenes = natsort.natsorted(os.listdir(RECEIVED))
# scenes = natsort.natsorted([i for i in scenes if 'normal' in i])

for id, scene in enumerate(scenes):
    dst = os.path.join(UNPACK_RAW, str(id).zfill(2) + '__' + scene.replace(' ', '').replace(',', '_').replace('.', 'p'))
    os.makedirs(dst, exist_ok=True)
    # files = natsort.natsorted(glob.glob(os.path.join(RECEIVED, scene, '*.RawPlain16LSB14bit')))
    # files = natsort.natsorted(glob.glob(os.path.join(RECEIVED, scene, 'Session*', '*.raw')))
    files = natsort.natsorted(glob.glob(os.path.join(RECEIVED, scene, '*.raw')))
    print(scene, len(files), end=' ')
    files = natsort.natsorted([i for i in files if os.path.getsize(i) == 16588800])
    print(len(files))
    for i, file in enumerate(files):
        img = np.fromfile(file, dtype = np.uint16)
        if 'output' not in scene:
            (img >> 4).tofile(os.path.join(dst, str(i).zfill(3) + '_' + os.path.basename(file)))
        else:
            shutil.move(file, os.path.join(dst, str(i).zfill(3) + '_' + os.path.basename(file)))
