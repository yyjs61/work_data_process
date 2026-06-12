from concurrent.futures import ThreadPoolExecutor
import subprocess, os, time

# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

# ROOT = '/data/030_Test_0327_for16-9_20260327/'
# ROOT = r"D:\Data\2026_05\13\030_dcg_lab_20260508/"
# ROOT = r'D:\Data\2026_06\04\030_4k60_quad_scg_outside_20260604/'
# ROOT = r"D:\Data\2026_06\05\20260604_2x_4k60_raw\030_4k60_quad_scg_day_20260605/"
# ROOT = r'D:\Data\2026_06\05\V210_OV50X_quad_night_20260519/'
# ROOT = r"D:\Data\2026_06\05\030_1x_dcg_sensor_raw_ev0_ev+_ev+2_3000k_20260605/"
# ROOT = r"D:\Data\2026_06\05\030_2x_4k30_quad_dcg_day_20260605/"
# ROOT = r"D:\Data\2026_06\10\030_4k60_quad_scg_20260610/"
ROOT = r"D:\Data\2026_06\11\HY_IMX06A_20260601/"

UNPACK_RAW = ROOT + 'unpack_raw'
scenes = sorted(os.listdir(UNPACK_RAW))

def run_scene(scene):
    cmd = f'python IMX06A/subp_VisualizeSensorRawAsRGB.py {scene}'
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

