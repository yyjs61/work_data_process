from concurrent.futures import ThreadPoolExecutor
import subprocess, os, time


# ROOT = r'D:\Data\20260423\honor/'
ROOT = r'D:\Data\2026_05\07\add_/'

UNPACK_RAW = ROOT + 'unpack_raw'
scenes = sorted(os.listdir(UNPACK_RAW))

def run_scene(scene):
    cmd = f'python v3_imx06c/subp_VisualizeSensorRawAsRGB.py {scene}'
    return subprocess.run(cmd, shell=True)

with ThreadPoolExecutor(max_workers=3) as executor:
    executor.map(run_scene, scenes)


