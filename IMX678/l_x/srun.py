import cv2, yaml, glob, os, sys, subprocess, numpy as np


# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

ROOT = r"D:\Data\2026_05\20\Test_data_260520\IMX678_Test_data_260520/"

UNPACK_RAW = ROOT + 'unpack_raw/'
YAML_DATA = ROOT + 'yamls_eachFrame/'

scenes = sorted(os.listdir(UNPACK_RAW))
for scene in scenes:
    # scene = os.path.join(UNPACK_RAW, scene)
    # subprocess.run(f'srun -p ISPCodec -n 1 --cpus-per-task=1 python APOM_IMX681_20250721/srun_VisualizeSensorRawAsRGB_12M.py {scene} &', shell=True)
    subprocess.Popen(f' python IMX678/VisualizeSensorRawAsRGB.py {scene}', shell=True)