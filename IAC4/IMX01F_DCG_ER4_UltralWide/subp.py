from concurrent.futures import ThreadPoolExecutor
import subprocess, os, time

# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

# ROOT = '/data/OVH9000_DCG_20260326_portrait/'
# ROOT = r'D:\Data\20260423\honor/'
# ROOT = r'D:\Data\2026_04\29\OVH9000_DCG_20260429_garage/'
# ROOT = r'D:\Data\2026_05\07\imx01f_EVT2p3_0040\IAC4_imx01f_EVT2p3_0040_sensor_raw_ultrawide_20260508/'
# ROOT = r'D:\Data\2026_05\22\IAC4_IMX01F_DCG_ER4_UltralWide_20260522/'
# ROOT = r'D:\Data\2026_05\25\IAC4_IMX01F_DCG_ER4_Wide_20260525/'
# ROOT = r'D:\Data\2026_05\26\IAC4_IMX01F_DCG_ER16_Wide_Night_dumpraw_20260526/'
ROOT = r'D:\Data\2026_05\29\IAC4_IMX01F_DCG_ER16_Wide_Night_dumpraw_20260529/' 
UNPACK_RAW = ROOT + 'unpack_raw'
scenes = sorted(os.listdir(UNPACK_RAW))

def run_scene(scene):
    cmd = f'python IAC4/IMX01F_DCG_ER4_UltralWide/subp_VisualizeSensorRawAsRGB.py {scene}'
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

