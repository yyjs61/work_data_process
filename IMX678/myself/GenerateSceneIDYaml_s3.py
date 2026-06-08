import glob, os, numpy as np

ROOT_PATH = './ROOT_PATH.txt'
with open(ROOT_PATH,'r') as file:
    ROOT = file.readline().strip()
if ROOT[-1] == '/':
  DATASET_NAME = os.path.basename(ROOT[:-1])

# DATASET_NAME = '20241106'
# ROOT = f'/mnt/lustrenew/share_data/cp/ProjectData/VideoSupernightData/input_data/CUA_OV50H/CUA_OV50H_DVT/20241113/'
RECEIVED = ROOT + 'received/'


EXAMPLE_YAML = '''
denoise_deghost_cfg:
  path: ./yaml/denoise_deghost_configs.yaml
fusion_cfg:
  flag: fusion3
  path: ./yaml/fusion_configs.yaml
postprocess_cfg:
  path: ./yaml/postprocess_configs.yaml

'''

'''
dir_name: /mnt/lustre/share/cp/ProjectData/VideoSupernightData/input_data/OV48C/CUA_OV48C_20231024/unpack_raw/raw_dump_1_decompress_5lux
eachframe_yaml_path: /mnt/lustre/share/cp/ProjectData/VideoSupernightData/input_data/OV48C/CUA_OV48C_20231024/yamls_eachFrame/raw_dump_1_decompress_5lux
'''

# LUSTER_ROOT = f'/mnt/lustre/share/cp/ProjectData/VideoSupernightData/input_data/IMX06C/{DATASET_NAME}'
LUSTER_ROOT = ROOT
if LUSTER_ROOT[-1] == '/':
    LUSTER_ROOT = LUSTER_ROOT[:-1]

# s3 = 's3://isp_projectdata/VideoSupernightData/Byte_OV50M'
# s3 = 's3://isp_projectdata/VideoSupernightData/AUTEL_OV50E'
# s3 = 's3://isp_projectdata/VideoSupernightData/CUA_OV50H'
# s3 = 's3://isp_projectdata/VideoSupernightData/C9'
# s3 = 's3://isp_projectdata/VideoSupernightData/PICO'
# s3 = 's3://isp_projectdata/VideoSupernightData/VIVO_XR'
# s3 = 's3://isp_projectdata/VideoSupernightData/looki_imx681'
# s3 = 's3://isp_projectdata/VideoSupernightData/APOM_IMX681'
# s3 = 's3://isp_projectdata/VideoSupernightData/TC101_SC5A0XS'
s3 = 's3://isp_projectdata/VideoSupernightData/VNT/IP_V2p5'
# s3 = 's3://isp_projectdata/VideoSupernightData/Ali_IMX681_A320'
# s3 = 's3://isp_projectdata/VideoSupernightData/Raw_compress'
# s3 = 's3://isp_projectdata/VideoSupernightData/V3_IMX06C'
# s3 = 's3://isp_projectdata/VideoSupernightData/Insta_IMX06A'
# s3 = 's3://isp_projectdata/VideoSupernightData/Insta_OV50Q'
# s3 = 's3://isp_projectdata/VideoSupernightData/Insta_TMC_IMX471'
# s3 = 's3://isp_projectdata/VideoSupernightData/DJI_ov68a'
# s3 = 's3://isp_projectdata/VideoSupernightData/DJI_OV50X'
# s3 = 's3://isp_projectdata/VideoSupernightData/HNR_OV50H'
# s3 = 's3://isp_share/dingshenglin'

unpack_raw = ROOT + 'unzipped'

# scenes = sorted(glob.glob(os.path.join(RECEIVED, '*.raw')))
scenes = sorted(os.listdir(unpack_raw))
for j, scene in enumerate(scenes):
    sub_scenes = os.listdir(os.path.join(unpack_raw, scene))
    for sub_scene in sub_scenes:
      ID_FOLDER = ROOT + 'SceneIDYaml/' + scene + '/'
      os.makedirs(ID_FOLDER, exist_ok=True)
      scene_name = os.path.basename(sub_scene)
      fo = open(os.path.join(ID_FOLDER, f'{scene_name}.yaml'), 'w')
      fo.write(EXAMPLE_YAML)
      fo.write(f'dir_name: {s3}/{os.path.basename(LUSTER_ROOT)}/unzipped/{scene}/{sub_scene}/long_unpack\n')
      fo.write(f'eachframe_yaml_path: {s3}/{os.path.basename(LUSTER_ROOT)}/yamls_eachFrame/{scene}/{sub_scene}\n')
      fo.close()
