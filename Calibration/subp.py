from concurrent.futures import ThreadPoolExecutor
import subprocess, os, time

# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

# ROOT = '/data/030_CALI_9_16_0326/'
# ROOT = '/home/user/afs_data/LeeSin_Xie/data/RatingData/'
# ROOT = r'D:\Data\2026_05\08\D-gain_calibration_data/'
# ROOT = r"D:\Data\2026_06\08\Honor_FPRO_TELE_QUAD_20260608_ER1/"
# ROOT = r"D:\Data\2026_06\10\ainr_MCC_BLC/"
ROOT = r"D:\Data\2026_06\11\HY_IMX06A_20260601\HY_IMX06A_20260611/"

# UNPACK_RAW = ROOT + 'BlackLevel'
UNPACK_RAW = ROOT + 'NoiseProfile'
scenes = sorted(os.listdir(UNPACK_RAW))

def run_scene(scene):
    cmd = f'python Calibration/subp_VisualizeSensorRawAsRGB.py {scene}'
    return subprocess.run(cmd, shell=True)

with ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(run_scene, scenes)

# import cv2, yaml, glob, os, sys, subprocess, numpy as np


# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()
# ROOT = '/data/20260228_AI-ISP-Calib-2026-03-02/'

# UNPACK_RAW = ROOT + 'BlackLevel/'
# # YAML_DATA = ROOT + 'yamls_eachFrame/'

# scenes = sorted(os.listdir(UNPACK_RAW))
# for scene in scenes:

#     subprocess.run(f'python data_process_demo/HONOR_DCG/subp_VisualizeSensorRawAsRGB.py {scene} &', shell=True)

