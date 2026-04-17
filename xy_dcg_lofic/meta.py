import glob, os, numpy as np
import yaml, natsort


# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

ROOT = '/data/SC5A0XS_DCGandLOFIC_20260211_inner/'

RECEIVED = ROOT + 'received/'
UNPACK_RAW = ROOT + 'unpack_raw/'
BAYER_PATTERN = 'BGGR'
W = 3840
H = 2160
WP = 16383
BP = 1024
## lux_index is not from real-time dump! BE VERY CAREFUL!!
EXAMPLE_META = '''
Black_level: 1024.0
White_level: 16383.0
bayer_pattern: BGGR
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
lux_index: 300.0
luxid: 300.0
cct: 4000
'''
KEY = 1.185
KEY = 1.172  # now

# meta txt 文件中某两行示例

def parseLine(line):
    key, value = line.strip().split('=')
    return int(value)


def parseMeta(meta_lofic, meta_dcg):
    result = {}
    result['expotime'] = parseLine(meta_dcg[4]) * 1000
    result['SensorAGain'] = min(parseLine(meta_dcg[6]) / 1024, 31.875)
    result['SensorDGain'] = parseLine(meta_dcg[7]) / 1024
    result['sensorgain'] = result['SensorAGain'] * result['SensorDGain']
    result['gain'] = result['sensorgain']
    result['isp_gain'] = parseLine(meta_dcg[5]) / 1024
    result['iso'] = int(result['SensorAGain'] * 100)

    result['under_expotime'] = parseLine(meta_lofic[4]) * 1000
    result['under_SensorAGain'] = min(parseLine(meta_lofic[6]) / 1024 * KEY, 8.0)
    result['under_SensorDGain'] = parseLine(meta_lofic[7]) / 1024
    result['under_sensorgain'] = result['under_SensorAGain'] * result['under_SensorDGain']
    result['under_gain'] = result['under_sensorgain']
    result['under_iso'] = int(result['under_SensorAGain'] * 100)


    return result

def get_awb_gain(file):
    img = np.fromfile(file, dtype=np.uint16).reshape([H, W]).astype(float)
    img = (img - BP) / (WP - BP)
    img = img.clip(0, 1)
    if BAYER_PATTERN == 'RGGB':
        sum_r = np.sum(img[0::2,0::2])
        sum_b = np.sum(img[1::2,1::2])
        sum_g = np.sum(img[0::2,1::2]) + np.sum(img[1::2,0::2])

        scale_r = max(1, sum_g/2/sum_r) 
        scale_b = max(1, sum_g/2/sum_b)

    elif BAYER_PATTERN == 'GBRG':
        sum_r = np.sum(img[1::2,0::2])
        sum_b = np.sum(img[0::2,1::2])
        sum_g = np.sum(img[0::2,0::2]) + np.sum(img[1::2,1::2])

        scale_r = max(1, sum_g/2/sum_r)
        scale_b = max(1, sum_g/2/sum_b)      

    elif BAYER_PATTERN == 'GRBG':
        sum_r = np.sum(img[0::2,1::2])
        sum_b = np.sum(img[1::2,0::2])
        sum_g = np.sum(img[0::2,0::2]) + np.sum(img[1::2,1::2])

        scale_r = max(1, sum_g/2/sum_r)
        scale_b = max(1, sum_g/2/sum_b)


    elif BAYER_PATTERN == 'BGGR':
        c1 = img[1::2,1::2]
        c2 = img[0::2,0::2]
        c3 = img[0::2,1::2]
        c4 = img[1::2,0::2]
        c1[c1 > (0.4 * WP)/WP] = 0
        c2[c2 > (0.4 * WP)/WP] = 0
        c3[c3 > (0.95 * WP)/WP] = 0
        c4[c4 > (0.95 * WP)/WP] = 0
        # print(np.max(c1))
        sum_r = np.sum(c1)
        sum_b = np.sum(c2)
        sum_g = np.sum(c3) + np.sum(c4)
        # sum_r = np.sum(img[1::2,1::2])
        # sum_b = np.sum(img[0::2,0::2])
        # sum_g = np.sum(img[0::2,1::2]) + np.sum(img[1::2,0::2])

        scale_r = max(1, sum_g/2/sum_r)
        scale_b = max(1, sum_g/2/sum_b)



    # print(scale_r, scale_b)
    return scale_r, scale_b


scenes = sorted(os.listdir(UNPACK_RAW))
# scenes = sorted(['03__lightbrand__ev0', '04__lightbrand__ev-', '05__lightbrand__ev-2'])
for j, scene in enumerate(scenes):
    scene_folder = os.path.join(ROOT, 'yamls_eachFrame', os.path.basename(scene))
    os.makedirs(scene_folder, exist_ok=True)

    
    meta_path_lofic = glob.glob(os.path.join(RECEIVED,scene.split('__')[1], '*WDR(VCNum0)*txt'))[0]
    meta_path_dcg = glob.glob(os.path.join(RECEIVED,scene.split('__')[1], '*WDR(VCNum1)*txt'))[0]

    fi = open(meta_path_lofic, 'r')
    lines_lofic = fi.readlines()[14:]
    fi.close()

    fi = open(meta_path_dcg, 'r')
    lines_dcg = fi.readlines()[14:]
    fi.close()
    imgs = sorted(glob.glob(os.path.join(UNPACK_RAW, scene, '*.raw')))
    for i in range(len(imgs)//2):
        meta_lofic = lines_lofic[i * 14: (i+1) * 14]
        meta_dcg = lines_dcg[i * 14: (i+1) * 14]

        assert i == int(meta_lofic[0].split(']')[0].split('e')[1])
        meta_result = parseMeta(meta_lofic, meta_dcg)

        with open(os.path.join(scene_folder, f'{str(i*2).zfill(3)}.yaml'), 'w') as fo:
            fo.write(EXAMPLE_META) 
            yaml.safe_dump(meta_result, stream=fo, default_flow_style=False)
            r_gain, b_gain = get_awb_gain(imgs[i*2 + 1])
            fo.write(f'r_gain: {r_gain}\n')
            fo.write(f'b_gain: {b_gain}\n')

        with open(os.path.join(scene_folder, f'{str(i*2 +1).zfill(3)}.yaml'), 'w') as fo:
            fo.write(EXAMPLE_META) 
            yaml.safe_dump(meta_result, stream=fo, default_flow_style=False)

            fo.write(f'r_gain: {r_gain}\n')
            fo.write(f'b_gain: {b_gain}\n')
        
        
