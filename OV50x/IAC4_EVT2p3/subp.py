
from concurrent.futures import ThreadPoolExecutor
import subprocess, os, time


# 定义根目录（请根据实际路径修改）
ROOT = r'C:\Users\admin.DESKTOP-QNCO006\Desktop\IAC4\IAC4_EVT2p3_QUAD_Wide_20260420/'

UNPACK_RAW = ROOT + 'unpack_raw'
scenes = sorted(os.listdir(UNPACK_RAW))

def run_scene(scene):
    cmd = f'python ./subp_VisualizeSensorRawAsRGB.py {scene}'
    return subprocess.run(cmd, shell=True)

with ThreadPoolExecutor(max_workers=3) as executor:
    executor.map(run_scene, scenes)