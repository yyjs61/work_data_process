from concurrent.futures import ThreadPoolExecutor
import subprocess, os, time


# ROOT = r'D:\Data\20260423\honor/'
# ROOT = r'D:\Data\2026_05\07\add_/'
# ROOT = r"D:\Data\2026_05\09\V3_imx06c_20260509/"
# ROOT = r"D:\Data\2026_05\12\V3_imx06c_20260512/"
# ROOT = r"D:\Data\2026_05\20\V3_imx06c_gen_meta_20260520/"
# ROOT = r"D:\Data\2026_05\20\V3_imx06c_20260520/"
# ROOT = r"D:\Data\2026_05\22\V3_imx06c_20260522/"
# ROOT = r"D:\Data\2026_05\22\blc_raw/"
# ROOT = r"D:\Data\2026_06\04\V3_imx06c_20260604/"
ROOT = r'D:\Data\2026_06\05\V210_OV50X_quad_night_20260519/'

UNPACK_RAW = ROOT + 'unpack_raw'
scenes = sorted(os.listdir(UNPACK_RAW))

def run_scene(scene):
    cmd = f'python v3_imx06c/subp_VisualizeSensorRawAsRGB.py {scene}'
    return subprocess.run(cmd, shell=True)

with ThreadPoolExecutor(max_workers=3) as executor:
    executor.map(run_scene, scenes)


