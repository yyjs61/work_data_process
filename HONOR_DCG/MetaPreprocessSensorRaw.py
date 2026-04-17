import glob, os, numpy as np
import yaml, natsort


# ROOT_PATH = './ROOT_PATH.txt'
# with open(ROOT_PATH,'r') as file:
#     ROOT = file.readline().strip()

ROOT = '/data/OVH9000_DCG_20260326_portrait/'
RECEIVED = ROOT + 'received/'


## lux_index is not from real-time dump! BE VERY CAREFUL!!
EXAMPLE_META = '''
Black_level: 64.0
White_level: 16383.0
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
bayer_pattern: RGGB

'''


# meta txt 文件中某两行示例

def parseLine(line):
    key, value = line.strip().split(':')
    return int(value) if not '.' in value else float(value)


def parseMeta(meta):
    result = {}
    result['expotime'] = int(parseLine(meta[2]) * 1000000)
    result['SensorAGain'] = parseLine(meta[4])
    result['SensorDGain'] = 1.0
    result['sensorgain'] = result['SensorAGain']
    result['gain'] = result['SensorAGain']
    result['isp_gain'] = parseLine(meta[5])
    result['drc_gain'] = parseLine(meta[6])
    result['iso'] = int(result['SensorAGain'] * 100)
    result['r_gain'] = parseLine(meta[8])
    result['b_gain'] = parseLine(meta[9])
    result['lux_index'] = parseLine(meta[3])
    result['luxid'] = parseLine(meta[3])
    result['cct'] = parseLine(meta[10])
    
    return result



unpack_raw = ROOT + 'unpack_raw'
scenes = sorted(os.listdir(unpack_raw))
for j, scene in enumerate(scenes):
    scene_folder = os.path.join(ROOT, 'yamls_eachFrame', os.path.basename(scene))
    os.makedirs(scene_folder, exist_ok=True)
    metas = natsort.natsorted(glob.glob(os.path.join(ROOT, 'received', scene.split('__')[1], '*.txt')))
    scene_raw = natsort.natsorted(glob.glob(os.path.join(unpack_raw, scene, '*.raw')))
    assert len(scene_raw) == len(metas)
    for i in range(len(metas)):
        with open(os.path.join(scene_folder, f'{str(i).zfill(3)}.yaml'), 'w') as fo:
            with open(metas[i], 'r') as fo_meta:
                lines = fo_meta.readlines()
            meta_result = parseMeta(lines)
            fo.write(EXAMPLE_META)
            yaml.safe_dump(meta_result, stream=fo, default_flow_style=False)
        
        
