import glob, os
import numpy as np
import xml.etree.ElementTree as ET
import yaml, natsort

# 保持原有的路径配置
# ROOT_PATH = './ROOT_PATH.txt'
# try:
#     with open(ROOT_PATH, 'r') as file:
#         ROOT = file.readline().strip()
# except FileNotFoundError:
#     # 如果找不到文件，使用硬编码路径
#     ROOT = r"D:\Data\2026_05\20\Test_data_260520\IMX678_Test_data_260520/"

# ROOT = ROOT if ROOT else r"D:\Data\2026_05\20\Test_data_260520\IMX678_Test_data_260520/"
# ROOT = r"D:\Data\2026_05\20\Test_data_260520\IMX678_Test_data_260520/"
ROOT = r"D:\Data\2026_05\21\IMX678_Test_data_260521/"

RECEIVED = ROOT + 'received/'
UNPACK_RAW = ROOT + 'unpack_raw/'
METADATA = ROOT + 'metadata/'

# 保持原有的传感器配置
BAYER_PATTERN = 'RGGB'
WP = 4095
BP = 200
H = 2160
W = 3840

EXAMPLE_META = '''
Black_level: 200
White_level: 4095
under_Black_level: 200
under_White_level: 4095
bayer_pattern: RGGB
isp_gain: 1.0
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
'''

def dB_to_gain(path):
    # if 'normal' in path:
    #     return 1
    default = 0
    if 'hcg' in path.lower():
        default += 8.35
    try:
        # 提取db数值
        dB = float(path.lower().split('db')[0].rsplit('_', 1)[1].replace('p', '.'))
        gain = 10 ** ((dB + default) / 20)
        return gain
    except:
        return 1.0

def parse_meta(path):
    result = {}
    
    # 解析 expotime (us)
    try:
        result['expotime'] = int(float(path.split('ms')[0].rsplit('_', 1)[1].replace('p', '.')) * 1000000)
    except:
        result['expotime'] = 0 # Fallback if parsing fails
        
    # 解析 gain
    result['SensorAGain'] = dB_to_gain(path)
    result['SensorDGain'] = 1.0
    result['sensorgain'] = result['SensorAGain'] * result['SensorDGain']
    result['gain'] = result['SensorAGain'] * result['SensorDGain']
    result['iso'] = int(result['SensorAGain'] * 50)  
    
    result['lux_index'] = 300
    result['luxid'] = result['lux_index']
    result['cct'] = 4000

    # ==================================================
    # 新增：添加 under_ 前缀的参数，数值与上方对应参数一致
    # ==================================================
    result['under_SensorAGain'] = result['SensorAGain']
    result['under_SensorDGain'] = result['SensorDGain']
    result['under_expotime'] = result['expotime']
    result['under_gain'] = result['gain']
    result['under_iso'] = result['iso']
    result['under_sensorgain'] = result['sensorgain']
    # ==================================================

    return result

def get_rgain_bgain(file):
    try:
        img = np.fromfile(file, dtype='uint16').reshape([H, W]).astype('float')
        img = (img - BP) / (WP - BP)
        img = img.clip(0, 1)

        if BAYER_PATTERN == 'RGGB':
            sum_r = np.sum(img[0::2, 0::2])
            sum_b = np.sum(img[1::2, 1::2])
            sum_g = np.sum(img[0::2, 1::2]) + np.sum(img[1::2, 0::2])
            scale_r = max(1, sum_g / 2 / sum_r) 
            scale_b = max(1, sum_g / 2 / sum_b)
        elif BAYER_PATTERN == 'GBRG':
            sum_r = np.sum(img[1::2, 0::2])
            sum_b = np.sum(img[0::2, 1::2])
            sum_g = np.sum(img[0::2, 0::2]) + np.sum(img[1::2, 1::2])
            scale_r = max(1, sum_g / 2 / sum_r)
            scale_b = max(1, sum_g / 2 / sum_b)
        elif BAYER_PATTERN == 'GRBG':
            sum_r = np.sum(img[0::2, 1::2])
            sum_b = np.sum(img[1::2, 0::2])
            sum_g = np.sum(img[0::2, 0::2]) + np.sum(img[1::2, 1::2])
            scale_r = max(1, sum_g / 2 / sum_r)
            scale_b = max(1, sum_g / 2 / sum_b)
        elif BAYER_PATTERN == 'BGGR':
            sum_r = np.sum(img[1::2, 1::2])
            sum_b = np.sum(img[0::2, 0::2])
            sum_g = np.sum(img[0::2, 1::2]) + np.sum(img[1::2, 0::2])
            scale_r = max(1, sum_g / 2 / sum_r)
            scale_b = max(1, sum_g / 2 / sum_b)
        else:
            return 1.0, 1.0
            
        return scale_r, scale_b
    except:
        return 1.0, 1.0

if __name__ == "__main__":
    scenes = sorted(os.listdir(os.path.join(ROOT, 'unpack_raw')))
    
    for j, scene in enumerate(scenes):
        scene_folder = os.path.join(ROOT, 'yamls_eachFrame', scene)
        os.makedirs(scene_folder, exist_ok=True)
        
        meta_result = parse_meta(os.path.basename(scene))
        files = natsort.natsorted(glob.glob(os.path.join(UNPACK_RAW, scene, '*.raw')))
        
        for i, file in enumerate(files):
            try:
                # 确保输出目录存在
                os.makedirs(scene_folder, exist_ok=True)
                
                with open(os.path.join(scene_folder, f'{str(i).zfill(3)}.yaml'), 'w') as fo:
                    fo.write(EXAMPLE_META)
                    
                    # 写入解析出的参数 (包含新增的 under_ 参数)
                    yaml.safe_dump(meta_result, stream=fo, default_flow_style=False)
                    
                    rgain, bgain = get_rgain_bgain(file)
                    fo.write(f'r_gain: {rgain}\n')
                    fo.write(f'b_gain: {bgain}\n')
            except Exception as e:
                print(f"Error processing {file}: {e}")