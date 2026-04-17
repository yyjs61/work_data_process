import os
import glob
import yaml
import re
import natsort


ROOT = '/data/SC590_dcg_20260317_ainr/'

UNPACK_RAW = os.path.join(ROOT, 'unpack_raw')
RECEIVED = os.path.join(ROOT, 'received')
YAML_ROOT = os.path.join(ROOT, 'yamls_eachFrame')

EXAMPLE_META = '''
Black_level: 1024.0
White_level: 16383.0
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
bayer_pattern: RGGB

'''

def parse_srt_meta(srt_path):
    with open(srt_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    blocks = re.split(r'\n\d+\n', content)

    frame_list = []

    for block in blocks:
        if '[iso:' not in block:
            continue

        result = {}

        # ISO - 需要clip到1600
        iso_match = re.search(r'\[iso:\s*(\d+)\]', block)
        if iso_match:
            iso_value = int(iso_match.group(1))
            # Clip ISO to max 1600
            result['iso'] = min(iso_value, 1600)
        else:
            result['iso'] = 1600  # 默认值，如果找不到ISO

        # Gain 相关
        linear_gain_match = re.search(r'\[linear gain:\s*\(([^)]+)\)\]', block)
        if linear_gain_match:
            r_gain, g_gain, b_gain = linear_gain_match.group(1).split(',')
            gain = float(r_gain)  # 使用R通道的gain作为参考
            result['gain'] = gain
            result['SensorAGain'] = gain
            result['sensorgain'] = gain
        else:
            result['gain'] = 16.0
            result['SensorAGain'] = 16.0
            result['sensorgain'] = 16.0

        # Sensor DGain
        result['SensorDGain'] = 1.0

        # ADRC gain
        adrc_match = re.search(r'\[adrc gain\s*\(([^)]+)\)\]', block)
        if adrc_match:
            result['isp_gain'] = float(adrc_match.group(1))
            result['drc_gain'] = float(adrc_match.group(1))
        else:
            result['isp_gain'] = 1.0
            result['drc_gain'] = 1.0


        # shutter -> expotime
        shutter_match = re.search(r'\[shutter:\s*1/([\d\.]+)\]', block)
        if shutter_match:
            shutter = float(shutter_match.group(1))
            result['expotime'] = int(1e9 / shutter)

        # RGBGain
        rgb_match = re.search(r'\[RGBGain:\s*\(([^)]+)\)\]', block)
        if rgb_match:
            r, g, b = rgb_match.group(1).split(',')
            result['r_gain'] = float(r) / 16000.0
            result['b_gain'] = float(b) / 16000.0

        # CT
        ct_match = re.search(r'\[ct:\s*(\d+)\]', block)
        if ct_match:
            result['cct'] = int(ct_match.group(1))

        # lux_idx
        lux_match = re.search(r'\[lux_idx:\s*([\d\.]+)\]', block)
        if lux_match:
            lux = float(lux_match.group(1))
            result['lux_index'] = lux
            result['luxid'] = lux


        frame_list.append(result)

    return frame_list

scenes = natsort.natsorted(os.listdir(UNPACK_RAW))

for scene in scenes:

    raw_scene_path = os.path.join(UNPACK_RAW, scene)
    real_scene = scene.split('__', 1)[1] if '__' in scene else scene
    srt_candidates = glob.glob(os.path.join(RECEIVED, real_scene, 'meta.[sS][rR][tT]'))
    srt_path = srt_candidates[0]

    print(f'Processing scene: {scene}')

    yaml_folder = os.path.join(YAML_ROOT, scene)
    os.makedirs(yaml_folder, exist_ok=True)

    raw_files = natsort.natsorted(glob.glob(os.path.join(raw_scene_path, '*.raw*')))
    frame_list = parse_srt_meta(srt_path)
    frame_list = frame_list[:len(raw_files)]

    for idx, raw_file in enumerate(raw_files):
        yaml_file = os.path.join(yaml_folder,f'{str(idx).zfill(3)}.yaml')
        with open(yaml_file, 'w') as fo:
            fo.write(EXAMPLE_META)
            yaml.safe_dump(frame_list[idx],stream=fo,default_flow_style=False)

print("Done.")