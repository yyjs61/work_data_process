import glob, os, numpy as np

# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

# ROOT = '/home/user/afs_data/wang/hnr_wide_ov52a_dcg_testdate_20260408/'
# ROOT = r'D:\Data\2026_05\29\OVH9000_DCG_20260529_lab_darkest_walking_camera_moving/'
# ROOT = r'D:\Data\2026_06\04\030_4k60_quad_scg_outside_20260604/'
# ROOT = r"D:\Data\2026_06\05\20260604_2x_4k60_raw\030_4k60_quad_scg_day_20260605/"
# ROOT = r"D:\Data\2026_06\05\030_2x_4k30_quad_dcg_day_20260605/"
ROOT = r'D:\Data\2026_06\07\IAC4_IMX01F_DCG_ER4_Wide_lab_20260608/'

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
# s3 = 's3://isp_projectdata/VideoSupernightData/030'
# s3 = 's3://isp_projectdata/VideoSupernightData/A210/OV50X/Quad'
# s3 = 's3://isp_projectdata/VideoSupernightData/A500_Benchmark/fusioncore'
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
