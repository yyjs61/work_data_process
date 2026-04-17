import cv2, yaml, glob, os, sys, subprocess, numpy as np


# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()
ROOT = '/data/imx06a/'

UNPACK_RAW = ROOT + 'unpack_raw/'
RECEIVED = ROOT + 'received/'
YAML_DATA = ROOT + 'yamls_eachFrame/'

scenes = sorted(os.listdir(UNPACK_RAW))
for scene in scenes:

    subprocess.run(f'python data_process_demo/PGC_MAIN_IMX06A_DCG/VisualizeSensorRawAsRGB.py {scene} &', shell=True)
