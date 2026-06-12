from concurrent.futures import ThreadPoolExecutor
import subprocess, os, time

# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

# ROOT = '/data/030_Test_0327_for16-9_20260327/'
ROOT = r"D:\Data\2026_06\10\SC532_SCG_10bit_ISP_simulation_demo_raw_20260610/"


UNPACK_RAW = ROOT + 'unpack_raw'
scenes = sorted(os.listdir(UNPACK_RAW))

def run_scene(scene):
    cmd = f'python MONDO/subp_VisualizeSensorRawAsRGB.py {scene}'
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

