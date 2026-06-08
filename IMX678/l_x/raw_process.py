import os,glob, natsort
import shutil, numpy as np

# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

ROOT = r"D:\Data\2026_05\20\Test_data_260520\IMX678_Test_data_260520"

RECEIVED = os.path.join(ROOT,'received')
UNPACK_RAW = os.path.join(ROOT,'unpack_raw')
scenes = sorted(os.listdir(RECEIVED))


for index,scene in enumerate(scenes):
    files = natsort.natsorted(glob.glob(os.path.join(RECEIVED,scene,'*.raw')))
    files = natsort.natsorted([i for i in files if os.path.getsize(i) == 16588800])
    dst = os.path.join(UNPACK_RAW, str(index).zfill(2) + '__' + scene)
    os.makedirs(dst,exist_ok=True)
    for i, file in enumerate(files):
        shutil.move(file, os.path.join(dst, str(i).zfill(3) + '_' + os.path.basename(file)))




 
