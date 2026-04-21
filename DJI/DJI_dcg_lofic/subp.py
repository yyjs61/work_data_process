from concurrent.futures import ThreadPoolExecutor
import subprocess, os, time

# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

# ROOT = '/data/50X_Lofic_Dcg_simulation_0417/'
ROOT = r"D:\Data\DJI_OV50X\20260420\20260417_dcg_lofic/"

UNPACK_RAW = ROOT + 'unpack_raw'
scenes = sorted(os.listdir(UNPACK_RAW))

def run_scene(scene):
    cmd = f'python DJI/DJi_dcg_lofic/subp_VisualizeSensorRawAsRGB.py {scene}'
    return subprocess.run(cmd, shell=True)

with ThreadPoolExecutor(max_workers=3) as executor:
    executor.map(run_scene, scenes)


#     import cv2, yaml, glob, os, sys, subprocess, numpy as np


# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()
# UNPACK_RAW = ROOT + 'unpack_raw/'
# YAML_DATA = ROOT + 'yamls_eachFrame/'

# scenes = sorted(os.listdir(UNPACK_RAW))
# for scene in scenes:

#     subprocess.run(f'python data_process_demo/HONOR_DCG/subp_VisualizeSensorRawAsRGB.py {scene} &', shell=True)

