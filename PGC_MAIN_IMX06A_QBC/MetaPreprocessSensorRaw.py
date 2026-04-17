import glob, os, numpy as np
import yaml, sys


ROOT_PATH = './ROOT_PATH.txt'
with open(ROOT_PATH,'r') as file:
    ROOT = file.readline().strip()
# ROOT = f'/mnt/lustrenew/share_data/cp/ProjectData/VideoSupernightData/input_data/CUA_OV50H/CUA_OV50H_DVT/20241113/'
RECEIVED = ROOT + 'received/'
UNPACK_RAW = ROOT + 'unpack_raw'

## lux_index is not from real-time dump! BE VERY CAREFUL!!
EXAMPLE_META = '''
Black_level: 64.0
White_level: 1023.0
bayer_pattern: RGGB
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
lux_index: 300.0
luxid: 300.0

'''
BAYER_PATTERN = 'RGGB'
BP = 64.0
WP = 1023.0
W = 3840
H = 2160

# meta txt 文件中某两行示例

# def parseLine(line):
#     gain, shutter = line.rsplit('-', 1)[1].split('_')
#     gain, shutter = float(gain.replace('p', '.')), int(shutter.replace('ns', '').replace('p', '.'))
#     return [gain, shutter]

def parseLine(line):
    gain = float(line.rsplit('x')[0].rsplit('_', 1)[1].replace('p', '.'))
    shutter = int(float(line.rsplit('ms')[0].rsplit('_', 1)[1].replace('p', '.')) * 1000000)
    # shutter = int(float(line.rsplit('ns')[0].rsplit('_', 1)[1].replace('p', '.')))
    return [gain, shutter]


def parseMeta(meta):
    result = {}
    result['expotime'] = parseLine(meta)[1]
    result['cct'] = 4000
    result['SensorAGain'] = parseLine(meta)[0]
    result['SensorDGain'] = 1.0
    result['sensorgain'] = result['SensorAGain']
    result['gain'] = result['SensorAGain']
    result['isp_gain'] = 1.0
    result['drc_gain'] = 1.0
    result['iso'] = int(result['SensorAGain'] * 100)    
    return result

def get_awb_gain(file):
    # img = np.fromfile(file,dtype=np.uint16).reshape([H,W]).astype(float)
    img = quad_bayer_to_raw(file)
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
        sum_r = np.sum(img[1::2,1::2])
        sum_b = np.sum(img[0::2,0::2])
        sum_g = np.sum(img[0::2,1::2]) + np.sum(img[1::2,0::2])

        scale_r = max(1, sum_g/2/sum_r)
        scale_b = max(1, sum_g/2/sum_b)
    # print(scale_r, scale_b)
    return scale_r, scale_b

def quad_bayer_to_raw(quad_bayer):
    quad_bayer = np.fromfile(quad_bayer,dtype=np.uint16).reshape([H,W]).astype(float)
    '''
        G R  g1 g2    
        B G  g3 g4
    '''
    raw = np.zeros([quad_bayer.shape[0]//2,quad_bayer.shape[1]//2],dtype=np.uint16).astype(float)

    g1_1 = quad_bayer[::4,::4]
    g1_2 = quad_bayer[::4,1::4]
    g1_3 = quad_bayer[1::4,::4]
    g1_4 = quad_bayer[1::4,1::4]
    raw[::2,::2] = (g1_1 + g1_2 + g1_3 + g1_4)/4

    r1 = quad_bayer[::4,2::4]
    r2 = quad_bayer[::4,3::4]
    r3 = quad_bayer[1::4,2::4]
    r4 = quad_bayer[1::4,3::4]
    raw[::2,1::2] = (r1 + r2 + r3 + r4)/4

    b1 = quad_bayer[2::4,::4]
    b2 = quad_bayer[2::4,1::4]
    b3 = quad_bayer[3::4,::4]
    b4 = quad_bayer[3::4,1::4]
    raw[1::2,::2] = (b1 + b2 + b3 + b4)/4

    g2_1 = quad_bayer[2::4,2::4]
    g2_2 = quad_bayer[2::4,3::4]
    g2_3 = quad_bayer[3::4,2::4]
    g2_4 = quad_bayer[3::4,3::4]
    raw[1::2,1::2] = (g2_1 + g2_2 + g2_3 + g2_4)/4

    return raw.astype(np.uint16)



scenes = sorted(os.listdir(UNPACK_RAW))
for j, scene in enumerate(scenes):
# scene = sys.argv[1]
    scene_folder = os.path.join(ROOT, 'yamls_eachFrame', os.path.basename(scene))
    os.makedirs(scene_folder, exist_ok=True)

    files = sorted(glob.glob(os.path.join(UNPACK_RAW, scene, '*.raw')))

    meta_result = parseMeta(scene)
    for i, file in enumerate(files):
        r_gain, b_gain = get_awb_gain(file)    
        # r_gain, b_gain = awb_gain[j]    
        with open(os.path.join(scene_folder, f'{str(i).zfill(3)}.yaml'), 'w') as fo:
            fo.write(EXAMPLE_META)
            yaml.safe_dump(meta_result, stream=fo, default_flow_style=False)
            fo.write(f'r_gain: {r_gain}\n')
            fo.write(f'b_gain: {b_gain}\n')
            
        
        
