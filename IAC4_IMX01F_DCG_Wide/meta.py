import glob
import os
import yaml
import natsort

ROOT_PATH = './ROOT_PATH.txt'
with open(ROOT_PATH,'r') as file:
    ROOT = file.readline().strip()

RECEIVED = os.path.join(ROOT, 'received')
UNPACK_RAW = os.path.join(ROOT, 'unpack_raw')


EXAMPLE_META = '''
Black_level: 64.0
White_level: 16383.0
height: 3600.0
width: 4096.0
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
bayer_pattern: RGGB

'''


def get_value(lines, key):
    for line in lines:
        if line.strip().startswith(key):
            return float(line.split(':')[1].strip())
    return 0.0

def parseMeta(lines, base_iso=100):
    result = {}

    exp_ns = get_value(lines, 'expTime(ns)')
    a_gain = get_value(lines, 'sensorGain')
    d_gain = 1.0 
    isp_gain = get_value(lines, 'ispGain')
    drc_gain = get_value(lines, 'drcGain')
    lux = get_value(lines, 'lux')

    r_gain = get_value(lines, 'awbRGain')
    b_gain = get_value(lines, 'awbBGain')
    cct = get_value(lines, 'awbCt')

    sensorgain = a_gain * d_gain
    gain = sensorgain
    iso = int(a_gain * base_iso)

    result['expotime'] = int(exp_ns)
    result['SensorAGain'] = a_gain
    result['SensorDGain'] = d_gain
    result['sensorgain'] = sensorgain
    result['gain'] = gain
    result['isp_gain'] = isp_gain
    result['drc_gain'] = drc_gain
    result['iso'] = iso
    result['r_gain'] = r_gain
    result['b_gain'] = b_gain
    result['lux_index'] = lux
    result['luxid'] = lux
    result['cct'] = cct

    return result


scenes = sorted(os.listdir(UNPACK_RAW))

for scene in scenes:

    scene_name_original = scene.split('__', 1)[1] 
    scene_folder = os.path.join(ROOT, 'yamls_eachFrame', scene)
    os.makedirs(scene_folder, exist_ok=True)

    scene_raw = natsort.natsorted(
        glob.glob(os.path.join(UNPACK_RAW, scene, '*.raw'))
    )

    all_txt = glob.glob(os.path.join(RECEIVED, scene_name_original, '*.txt'))
    metas = [t for t in all_txt if os.path.basename(t).split('.')[0].isdigit()]
    metas = natsort.natsorted(metas)

    assert len(scene_raw) == len(metas)

    for i in range(len(metas)):

        with open(metas[i], 'r') as fo_meta:
            lines = fo_meta.readlines()

        meta_result = parseMeta(lines)

        yaml_path = os.path.join(scene_folder, f'{str(i).zfill(3)}.yaml')

        with open(yaml_path, 'w') as fo:
            fo.write(EXAMPLE_META)
            yaml.safe_dump(meta_result, stream=fo, default_flow_style=False)

