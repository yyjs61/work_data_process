import os, glob, natsort, shutil, numpy as np

ROOT_PATH = './ROOT_PATH.txt'
with open(ROOT_PATH,'r') as file:
    ROOT = file.readline().strip()
RECEIVED = ROOT + 'received/'

WIDTH = 3840
HEIGHT = 2160

scenes = natsort.natsorted(os.listdir(RECEIVED))
for id, scene in enumerate(scenes):
    dir = os.path.join(ROOT, 'unpack_raw', str(id).zfill(2) + '__' + scene.replace(' ', '_').replace(',', '_').replace('.', 'p'))
    os.makedirs(dir, exist_ok=True)
    
    imgs = natsort.natsorted(glob.glob(os.path.join(RECEIVED, scene, '*.raw')))
    imgs = natsort.natsorted([i for i in imgs if os.path.getsize(i) == 16588800])
    need_rotate = 'sensor_raw' in scene
    
    print(f"Processing: {scene} -> Rotate: {need_rotate}")
    
    for i, img in enumerate(imgs):
        raw = np.fromfile(img, dtype=np.uint16)
        
        if need_rotate:
            raw_2d = raw.reshape(HEIGHT, WIDTH)
            raw_rotated = np.rot90(raw_2d, 2)  
            
            raw_rotated.flatten().tofile(os.path.join(dir, str(i).zfill(3) + '_' + os.path.basename(img)))
            print(f"  Rotated (180°): {os.path.basename(img)}")
        else:
            raw.tofile(os.path.join(dir, str(i).zfill(3) + '_' + os.path.basename(img)))
            print(f"  Copied: {os.path.basename(img)}")