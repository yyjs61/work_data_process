import glob, os, numpy as np

# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

# ROOT = '/home/user/afs_data/wang/hnr_wide_ov52a_dcg_testdate_20260408/'
ROOT = '/home/user/afs_data/LeeSin_Xie/Quad_dag_20260409/'

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

# s3 = 's3://isp_projectdata/VideoSupernightData/HNR_RP_OV52a'
# s3 = 's3://isp_projectdata/Calibration/_CalibrationLSC/OBSBOT_SC5A0XS'
# s3 = 's3://isp_share/wangyuemei/test_data'
s3 = 's3://isp_projectdata/VideoSupernightData/DJI_OV50X'

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
