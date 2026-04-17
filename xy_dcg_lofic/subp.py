import cv2, yaml, glob, os, sys, subprocess, numpy as np


# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()
ROOT = '/data/SC5A0XS_DCGandLOFIC_20260211_inner/'

UNPACK_RAW = ROOT + 'unpack_raw/'
YAML_DATA = ROOT + 'yamls_eachFrame/'

scenes = sorted(os.listdir(UNPACK_RAW))
scene_str = "\n".join(scenes)
subprocess.run('parallel -j 7 python data_process_demo/xy_dcg_lofic/subp_VisualizeSensorRawAsRGB.py ::: ' + ' '.join(scenes), shell=True)