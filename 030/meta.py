import os
import glob
import yaml
import re
import natsort

ROOT = '/data/030_Test_0227_20260228/'

UNPACK_RAW = os.path.join(ROOT, 'unpack_raw')
YAML_ROOT  = os.path.join(ROOT, 'yamls_eachFrame')

EXAMPLE_META = '''
Black_level: 64.0
White_level: 16383.0
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
bayer_pattern: BGGR

'''

def parse_scene_name(scene_name):

    if '__' in scene_name:
        scene_name = scene_name.split('__', 1)[1]

    parts = scene_name.split('_')

    result = {}

    # shutter (10ms → ns)
    shutter_match = re.match(r'(\d+)ms', parts[1])
    if shutter_match:
        shutter_ms = int(shutter_match.group(1))
        result['expotime'] = shutter_ms * 1_000_000

    # again → gain
    again_match = re.match(r'(\d+)x', parts[2])
    if again_match:
        gain = float(again_match.group(1))
    else:
        gain = 1.0

    result['gain'] = gain
    result['SensorAGain'] = gain
    result['sensorgain'] = gain

    # iso = gain * 100
    result['iso'] = int(gain * 100)

    # 固定参数
    result['SensorDGain'] = 1.0
    result['isp_gain'] = 1.0
    result['drc_gain'] = 1.0
    result['b_gain'] = 2.168
    result['r_gain'] = 2.056

    # 新增固定项
    result['cct'] = 4000
    result['lux_index'] = 400.0
    result['luxid'] = 400.0

    return result


# =========================
# 主流程
# =========================

scenes = natsort.natsorted(
    [d for d in os.listdir(UNPACK_RAW)
     if os.path.isdir(os.path.join(UNPACK_RAW, d))]
)

for scene in scenes:

    print(f'\nProcessing scene: {scene}')

    raw_scene_path = os.path.join(UNPACK_RAW, scene)
    yaml_folder = os.path.join(YAML_ROOT, scene)
    os.makedirs(yaml_folder, exist_ok=True)

    raw_files = natsort.natsorted(
        glob.glob(os.path.join(raw_scene_path, '*.raw*'))
    )

    meta_info = parse_scene_name(scene)

    for idx in range(len(raw_files)):

        yaml_file = os.path.join(
            yaml_folder,
            f'{str(idx).zfill(3)}.yaml'
        )

        with open(yaml_file, 'w') as fo:
            fo.write(EXAMPLE_META)
            yaml.safe_dump(
                meta_info,
                stream=fo,
                default_flow_style=False
            )

print("\nDone.")