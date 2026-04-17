import os, glob, natsort, shutil, numpy as np

ROOT_PATH = './ROOT_PATH.txt'
with open(ROOT_PATH,'r') as file:
    ROOT = file.readline().strip()
RECEIVED = ROOT + 'received/'
MIPI_RAW = ROOT + 'unpack_raw/'

scenes = natsort.natsorted(os.listdir(RECEIVED))
for id, scene in enumerate(scenes):
    # dir = os.path.join(MIPI_RAW, str(id).zfill(2) + '__' + scene.replace(' ', '').replace(',', '_').replace('.', 'p'))
    dir = os.path.join(ROOT, 'unpack_raw', str(id).zfill(2) + '__' + scene.replace(' ', '_').replace(',', '_').replace('.', 'p'))
    os.makedirs(dir, exist_ok=True)
    # imgs = natsort.natsorted(glob.glob(os.path.join(RECEIVED, scene, '*.RawPlain16LSB10bit')))
    # imgs = natsort.natsorted(glob.glob(os.path.join(RECEIVED, scene, '*.RawPlain16LSB14bit')))
    imgs = natsort.natsorted(glob.glob(os.path.join(RECEIVED, scene, '*.raw')))
    imgs = natsort.natsorted([i for i in imgs if os.path.getsize(i) == 16588800])
    for i, img in enumerate(imgs):
        # raw = np.fromfile(img, dtype = np.uint16)[:-1536]
        # raw.tofile(os.path.join(dir, str(i).zfill(3) + '_' + os.path.basename(img)))      
        # shutil.move(img, os.path.join(dir, str(i).zfill(3) + '_' + os.path.basename(img) + '.raw'))
        shutil.copy(img, os.path.join(dir, str(i).zfill(3) + '_' + os.path.basename(img)))
