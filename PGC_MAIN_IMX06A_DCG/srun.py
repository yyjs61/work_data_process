import cv2, yaml, glob, os, sys, subprocess, numpy as np


# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()
# ROOT = '/data/imx06a/'
# ROOT = r'E:\0512/'
# ROOT = r'D:\Data\2026_05\19\0519/'


# UNPACK_RAW = ROOT + 'unpack_raw/'
# RECEIVED = ROOT + 'received/'
# YAML_DATA = ROOT + 'yamls_eachFrame/'

# scenes = sorted(os.listdir(UNPACK_RAW))
# for scene in scenes:

#     subprocess.run(f'python PGC_MAIN_IMX06A_DCG/VisualizeSensorRawAsRGB.py {scene} &', shell=True)

# ROOT = r'D:\Data\2026_05\19\IMX06C_binning_normal_4k_20260514/'

from concurrent.futures import ThreadPoolExecutor
import subprocess, os, time

ROOT = r'D:\Data\2026_05\19\0519_2/'

UNPACK_RAW = ROOT + 'unpack_raw'
scenes = sorted(os.listdir(UNPACK_RAW))

def run_scene(scene):
    cmd = f'python PGC_MAIN_IMX06A_DCG/VisualizeSensorRawAsRGB.py {scene}'
    print(scene)
    return subprocess.run(cmd, shell=True)

with ThreadPoolExecutor(max_workers=3) as executor:
    executor.map(run_scene, scenes)

    import cv2, yaml, glob, os, sys, subprocess, numpy as np
