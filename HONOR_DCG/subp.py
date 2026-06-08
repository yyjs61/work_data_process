
from concurrent.futures import ThreadPoolExecutor
import subprocess, os, time

# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

# ROOT = "/home/user/afs_data/ACEPro2/OVH9000_DCG_20260417_low_light/honor/"
ROOT = r'D:\Data\2026_05\29\NR_iterative_data_20260529/'

# ROOT = '/data/0310_hnr_tele_hp3_quad_texture2/'

UNPACK_RAW = ROOT + 'unpack_raw'
scenes = sorted(os.listdir(UNPACK_RAW))

def run_scene(scene):
    cmd = f'python HONOR_DCG/subp_VisualizeSensorRawAsRGB.py {scene}'
    print(scene)
    return subprocess.run(cmd, shell=True)

with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(run_scene, scenes)