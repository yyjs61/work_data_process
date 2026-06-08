
import glob, os,numpy as np
import xml.etree.ElementTree as ET

import yaml, natsort


# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()
# ROOT = '/mnt/lustre/share/cp/ProjectData/VideoSupernightData/input_data/CUA_OV50H/CUA_OV50H_PVT/20241112_zhulongxin/'
ROOT = r"D:\Data\2026_05\20\Test_data_260520\IMX678_Test_data_260520/"

RECEIVED = ROOT + 'received/'
UNPACK_RAW = ROOT + 'unpack_raw/'
METADATA = ROOT + 'metadata/'
BAYER_PATTERN = 'RGGB'
WP = 4095
BP = 200
H = 2160   
W = 3840


EXAMPLE_META = '''
Black_level: 200
White_level: 4095
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
    dB = float(path.lower().split('db')[0].rsplit('_',1)[1].replace('p', '.'))
    gain = 10 ** ((dB+default)/20)
    return gain
    


def parse_meta(path):
    result = {}

    result['expotime'] = int(float(path.split('ms')[0].rsplit('_',1)[1].replace('p', '.')) * 1000000)
    result['SensorAGain'] = dB_to_gain(path)
    result['SensorDGain'] = 1.0
    result['sensorgain'] = result['SensorAGain'] * result['SensorDGain']
    result['gain'] = result['SensorAGain'] * result['SensorDGain']
    result['iso'] = int(result['SensorAGain'] * 50)  
    result['lux_index'] = 300
    result['luxid'] = result['lux_index']
    result['cct'] = 4000
    return result

def get_rgain_bgain(file):
    img = np.fromfile(file, dtype='uint16').reshape([H, W]).astype('float')
    img = (img - BP) / (WP - BP)
    img = img.clip(0,1)
    if BAYER_PATTERN == 'RGGB':
        sum_r = np.sum(img[0::2,0::2])
        sum_b = np.sum(img[1::2,1::2])
        sum_g = np.sum(img[0::2,1::2]) + np.sum(img[1::2,0::2])

        scale_r = max(1, sum_g/2/sum_r) 
        scale_b = max(1, sum_g/2/sum_b)

        img[0::2,0::2] *= scale_r
        img[1::2,1::2] *= scale_b

    elif BAYER_PATTERN == 'GBRG':
        sum_r = np.sum(img[1::2,0::2])
        sum_b = np.sum(img[0::2,1::2])
        sum_g = np.sum(img[0::2,0::2]) + np.sum(img[1::2,1::2])

        scale_r = max(1, sum_g/2/sum_r)
        scale_b = max(1, sum_g/2/sum_b)      

        img[1::2,0::2] *= scale_r
        img[0::2,1::2] *= scale_b
    elif BAYER_PATTERN == 'GRBG':
        sum_r = np.sum(img[0::2,1::2])
        sum_b = np.sum(img[1::2,0::2])
        sum_g = np.sum(img[0::2,0::2]) + np.sum(img[1::2,1::2])

        scale_r = max(1, sum_g/2/sum_r)
        scale_b = max(1, sum_g/2/sum_b)

        img[0::2,1::2] *= scale_r
        img[1::2,0::2] *= scale_b 

    elif BAYER_PATTERN == 'BGGR':
        sum_r = np.sum(img[1::2,1::2])
        sum_b = np.sum(img[0::2,0::2])
        sum_g = np.sum(img[0::2,1::2]) + np.sum(img[1::2,0::2])

        scale_r = max(1, sum_g/2/sum_r)
        scale_b = max(1, sum_g/2/sum_b)
            
        img[1::2,1::2] *= scale_r
        img[0::2,0::2] *= scale_b
    # print(scale_r,scale_b)
    return scale_r,scale_b



scenes = sorted(os.listdir(os.path.join(ROOT,'unpack_raw')))
for j, scene in enumerate(scenes):
    scene_folder = os.path.join(ROOT, 'yamls_eachFrame', scene)
    os.makedirs(scene_folder, exist_ok=True)
    meta_result = parse_meta(os.path.basename(scene))
    files = natsort.natsorted(glob.glob(os.path.join(UNPACK_RAW, scene, '*.raw')))
    for i, file in enumerate(files):
        try:
            with open(os.path.join(scene_folder, f'{str(i).zfill(3)}.yaml'), 'w') as fo:
                fo.write(EXAMPLE_META)    
                yaml.safe_dump(meta_result, stream=fo, default_flow_style=False)
                rgain, bgain = get_rgain_bgain(file)
                fo.write(f'r_gain: {rgain}\n')
                fo.write(f'b_gain: {bgain}\n')
        except:
            print(files[i])


   
         

