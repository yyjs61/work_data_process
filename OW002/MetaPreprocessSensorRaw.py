import os, glob, yaml, natsort

ROOT = '/data/SC590_dcg_20260319_sensorraw/'
UNPACK_RAW = os.path.join(ROOT, 'unpack_raw')

EXAMPLE_META = '''
Black_level: 1024.0
White_level: 16383.0
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
bayer_pattern: RGGB

'''

def generate_frame_meta(frame_idx):

    result = {}

    iso = 1600
    gain = iso / 1600.0
    result['iso'] = iso
    result['SensorAGain'] = gain
    result['sensorgain'] = gain
    result['gain'] = gain
    result['SensorDGain'] = 1.0

    result['expotime'] = 10000000 

    result['r_gain'] = 2.056
    result['b_gain'] = 2.168

    result['lux_index'] = 443.0
    result['luxid'] = 443.0

    result['cct'] = 4000

    result['isp_gain'] = 1.0
    result['drc_gain'] = 1.0

    return result


scenes = natsort.natsorted(os.listdir(UNPACK_RAW))

for scene in scenes:
    scene_path = os.path.join(UNPACK_RAW, scene)
    yaml_folder = os.path.join(ROOT, 'yamls_eachFrame', scene)
    os.makedirs(yaml_folder, exist_ok=True)

    raw_files = natsort.natsorted(glob.glob(os.path.join(scene_path, '*.raw')))
    for frame_idx, raw_file in enumerate(raw_files):
        result = generate_frame_meta(frame_idx)
        yaml_file = os.path.join(yaml_folder, f'{str(frame_idx).zfill(3)}.yaml')
        with open(yaml_file, 'w') as fo:
            fo.write(EXAMPLE_META)
            yaml.safe_dump(result, stream=fo, default_flow_style=False)
