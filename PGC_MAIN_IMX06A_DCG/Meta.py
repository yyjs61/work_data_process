import glob
import os
import numpy as np
import yaml
import sys
import natsort


ROOT_PATH = './ROOT_PATH.txt'
with open(ROOT_PATH, 'r') as file:
    ROOT = file.readline().strip()

RECEIVED = ROOT + 'received/'
UNPACK_RAW = ROOT + 'unpack_raw'

## lux_index is not from real-time dump! BE VERY CAREFUL!!
EXAMPLE_META = '''
Black_level: 1024.0
White_level: 16383.0
bayer_pattern: RGGB
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
lux_index: 300.0
luxid: 300.0

'''


def parseLine(meta):
    with open(meta, 'r') as fo:
        line = fo.readline().strip()
        cct = int(line.split('CCT: ')[1].split(' ')[0])
        r_gain = float(line.split('RGain: ')[1].split(' ')[0])
        b_gain = float(line.split('BGain: ')[1].split(' ')[0])
    return [cct, r_gain, b_gain]


def parseLine2(meta):
    with open(meta, 'r') as fo:
        line = fo.readline().strip()
        expotime = int(line.split('exposureTime: ')[1].split(' ')[0])
        SensorAGain = min((float(line.split('sensitivity: ')[1].split(' ')[0]) / 100), 4.0)
        isp_gain = float(line.split('ISPDGain: ')[1].split(' ')[0])
    return [expotime, SensorAGain, isp_gain]


def parseMeta(meta, meta2):
    result = {}
    result['expotime'] = parseLine2(meta2)[0]
    result['cct'] = parseLine(meta)[0]
    result['SensorAGain'] = parseLine2(meta2)[1]
    result['SensorDGain'] = 1.0
    result['sensorgain'] = result['SensorAGain']
    result['gain'] = result['SensorAGain']
    result['isp_gain'] = parseLine2(meta2)[2]
    result['drc_gain'] = 1.0
    result['iso'] = int(result['SensorAGain'] * 100)
    result['r_gain'] = parseLine(meta)[1]
    result['b_gain'] = parseLine(meta)[2]
    return result


scenes = sorted(os.listdir(UNPACK_RAW))

for scene in scenes:
    scene_folder = os.path.join(ROOT, 'yamls_eachFrame', scene)
    os.makedirs(scene_folder, exist_ok=True)

    raw_files = natsort.natsorted(
        glob.glob(os.path.join(UNPACK_RAW, scene, '*.raw'))
    )

    recv_scene = scene.split('__')[1]

    awb_txts = natsort.natsorted(
        glob.glob(
            os.path.join(RECEIVED, recv_scene, '**', 'awb_output_cam*_req_*.txt'),
            recursive=True
        )
    )

    sensor_txts = natsort.natsorted(
        glob.glob(
            os.path.join(RECEIVED, recv_scene, '**', 'sensor_info_cam*_req_*.txt'),
            recursive=True
        )
    )

    print(
        f'[INFO] {scene}: raw={len(raw_files)}, '
        f'awb={len(awb_txts)}, sensor={len(sensor_txts)}'
    )

    min_len = min(len(raw_files), len(awb_txts), len(sensor_txts))

    for i in range(min_len):
        yaml_path = os.path.join(scene_folder, f'{str(i).zfill(3)}.yaml')

        with open(yaml_path, 'w') as fo:
            fo.write(EXAMPLE_META)
            meta_result = parseMeta(awb_txts[i], sensor_txts[i])
            yaml.safe_dump(meta_result, stream=fo, default_flow_style=False)

        # 可选 debug
        # print(f'frame {i}: {os.path.basename(awb_txts[i])} | {os.path.basename(sensor_txts[i])}')

    if len(raw_files) != min_len:
        print(f'⚠ raw 多于 txt，后 {len(raw_files) - min_len} 帧未生成 yaml')
