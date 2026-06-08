import glob, os, numpy as np

# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

# ROOT = '/home/user/afs_data/wang/hnr_wide_ov52a_dcg_testdate_20260408/'
# ROOT = r'D:\Data\DJI_OV50X\20260420\20260417_portrait/'
# ROOT = r"D:\Data\DJI_OV50X\20260420\20260417_dcg_lofic/"
# ROOT = r"D:\Data\DJI_OV50X\20260423\20260423_Simulation_materials/"
# ROOT = r'D:\Data\20260423\VAI_OVH9000_Magic7Pro_20260423/'
# ROOT = r'D:\Data\2026_04\29\OVH9000_DCG_20260429_garage/'
# ROOT = r'D:\Data\2026_05\06\V3_imx06c_20260506/'
# ROOT = r"D:\Data\DJI_OV50X\20260506\v2_data_20260506-2026-05-06\quad_day_20260506/"
# ROOT = r'D:\Data\2026_05\09\V3_imx06c_20260509/'
# ROOT = r'D:\Data\2026_05\07\imx01f_EVT2p3_0040\IAC4_imx01f_EVT2p3_0040_sensor_raw_ultrawide_20260508/'
# ROOT = r"D:\Data\DJI_OV50X\20260509\DJI_8xx_4096x2304_20260511/"
# ROOT = r"D:\Data\2026_05\12\V3_imx06c_20260512/"
# ROOT = r"D:\Data\DJI_OV50X\20260513\0511_ov50x_raw-2026-05-13\20260513_material/"
# ROOT = r'D:\Data\2026_05\19\IMX06C_binning_normal_4k_20260514/'
# ROOT = r"D:\Data\2026_05\20\V3_imx06c_gen_meta_20260520/"
# ROOT = r"D:\Data\2026_05\20\Test_data_260520\IMX678_Test_data_260520/"
# ROOT = r"D:\Data\2026_05\21\IMX678_Test_data_260521/"
# ROOT = r"D:\Data\2026_05\22\V3_imx06c_blc_raw_20260522/"
# ROOT = r'D:\Data\2026_05\22\IAC4_IMX01F_DCG_ER4_UltralWide_20260522/'
ROOT = r'D:\Data\2026_06\IAC4_IMX01F_DCG_ER4_Wide_Night_dumpraw_20260601/'


if ROOT[-1] == '/':
  DATASET_NAME = os.path.basename(ROOT[:-1])

RECEIVED = ROOT + 'received/'
ID_FOLDER = ROOT + 'SceneIDYaml/' + DATASET_NAME + '/'

EXAMPLE_YAML = '''
denoise_deghost_cfg:
  path: ./yaml/denoise_deghost_configs.yaml
fusion_cfg:
  flag: fusion3
  path: ./yaml/fusion_configs.yaml
postprocess_cfg:
  path: ./yaml/postprocess_configs.yaml

'''


LUSTER_ROOT = ROOT
if LUSTER_ROOT[-1] == '/':
    LUSTER_ROOT = LUSTER_ROOT[:-1]

# s3 = 's3://isp_projectdata/VideoSupernightData/8xx'
s3 = 's3://isp_projectdata/VideoSupernightData/IAC4'
# s3 = 's3://isp_projectdata/VideoSupernightData/DJI_OV50X'
# s3 = 's3://isp_projectdata/VideoSupernightData/V3_IMX06C'
# s3 = 's3://isp_projectdata/VideoSupernightData/VNT/IP_V2p5'

# s3 = 's3://isp_projectdata/VideoSupernightData/A500_Benchmark/aitone'
# s3 = 's3://isp_projectdata/VideoSupernightData/VAI'
# s3 = 's3://isp_projectdata/Calibration/_CalibrationLSC/OBSBOT_SC5A0XS'
# s3 = 's3://isp_share/wangyuemei/test_data'

# s3 = 's3://isp_projectdata/VideoSupernightData/DJI_OV50X'
unpack_raw = ROOT + 'unpack_raw'
os.makedirs(ID_FOLDER, exist_ok=True)
scenes = sorted(os.listdir(unpack_raw))
for j, scene in enumerate(scenes):
    scene_name = os.path.basename(scene)
    fo = open(os.path.join(ID_FOLDER, f'{scene_name}.yaml'), 'w')
    fo.write(EXAMPLE_YAML)
    fo.write(f'dir_name: {s3}/{os.path.basename(LUSTER_ROOT)}/unpack_raw/{scene_name}\n')
    fo.write(f'eachframe_yaml_path: {s3}/{os.path.basename(LUSTER_ROOT)}/yamls_eachFrame/{scene_name}\n')
    fo.close()
