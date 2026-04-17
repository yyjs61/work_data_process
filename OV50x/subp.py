# # import cv2, yaml, glob, os, sys, subprocess, numpy as np


# # ROOT_PATH = './ROOT_PATH.txt'
# # with open(ROOT_PATH,'r') as file:
# #     ROOT = file.readline().strip()
# # UNPACK_RAW = ROOT + 'unpack_raw/'
# # YAML_DATA = ROOT + 'yamls_eachFrame/'

# # scenes = sorted(os.listdir(UNPACK_RAW))
# # for scene in scenes:

# #     subprocess.run(f'python HONOR_DCG/subp_VisualizeSensorRawAsRGB.py {scene} &', shell=True)

# from concurrent.futures import ThreadPoolExecutor
# import subprocess, os, time

# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

# # ROOT = '/home/user/afs_data/OVH9000_DCG_20260311_exposure_hand/'
# # ROOT_PATH = './ROOT_PATH.txt'
# UNPACK_RAW = ROOT + 'unpack_raw'
# scenes = sorted(os.listdir(UNPACK_RAW))

# def run_scene(scene):
#     cmd = f'python HONOR_DCG/subp_VisualizeSensorRawAsRGB.py {scene}'
#     return subprocess.run(cmd, shell=True)

# with ThreadPoolExecutor(max_workers=3) as executor:
#     executor.map(run_scene, scenes)
# ++++++++++++++++++
# import cv2, yaml, glob, os, sys, subprocess, numpy as np


# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()
# UNPACK_RAW = ROOT + 'unpack_raw/'
# YAML_DATA = ROOT + 'yamls_eachFrame/'

# scenes = sorted(os.listdir(UNPACK_RAW))
# for scene in scenes:
#     subprocess.run(f'python HONOR_DCG/subp_VisualizeSensorRawAsRGB.py {scene} &', shell=True)

from concurrent.futures import ThreadPoolExecutor
import subprocess, os, time

# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

ROOT = r'C:\Users\admin.DESKTOP-QNCO006\Desktop\Data\OV50X\OV50X_DCGandLOFIC_20260410__lab_ipad/'

UNPACK_RAW = ROOT + 'unpack_raw'
scenes = sorted(os.listdir(UNPACK_RAW))

def run_scene(scene):
    cmd = f'python ./subp_VisualizeSensorRawAsRGB.py {scene}'
    return subprocess.run(cmd, shell=True)

with ThreadPoolExecutor(max_workers=3) as executor:
    executor.map(run_scene, scenes)