import os
import glob
import yaml
import natsort
import numpy as np
import re

# --- 配置参数 ---
# ROOT = '/data/V210_OV50X_Lofic_empty_shot_20260603/'
ROOT = r'D:\Data\2026_06\05\V210_OV50X_Lofic_human_face_20260603/'
RECEIVED = os.path.join(ROOT, 'received')
UNPACK_RAW = os.path.join(ROOT, 'unpack_raw')
YAML_ROOT = os.path.join(ROOT, 'yamls_eachFrame')

# DCG 参数
DCG_BP = 256.0
DCG_WP = 16383.0

# Lofic 参数
LOFIC_BP = 256.0
LOFIC_WP = 4095.0

BAYER_PATTERN = 'BGGR'
H = 2240
W = 3968

EXAMPLE_META = f'''
Black_level: {DCG_BP}
White_level: {DCG_WP}
under_Black_level: {LOFIC_BP}
under_White_level: {LOFIC_WP}
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
bayer_pattern: {BAYER_PATTERN}
lux_index: 443.0
luxid: 443.0
cct: 4000
'''

# 定义场景的 gain 和 sens_ratio 映射 (cct 和 wbc 将从 txt 读取)
SCENE_METADATA = {
    '00__0054': {
        'sens_ratio': 22.625,
        'dcg_a_gain': 11.07,
        'lofic_gain': 11.07,
    },
    '01__0089': {
        'sens_ratio': 8,
        'dcg_a_gain': 1.509,
        'lofic_gain': 1.071,
    },
    '02__0244': {
        'sens_ratio': 32,
        'dcg_a_gain': 2.384,
        'lofic_gain': 1.714,
    },
}

KEY = 1.0 

def parse_txt_meta(txt_path):
    """
    解析 received 目录下的 txt 文件，提取 cct, wbc 等信息
    """
    meta = {}
    try:
        with open(txt_path, 'r') as f:
            content = f.read()
            
        # 1. 尝试使用 yaml 解析
        data = yaml.safe_load(content)
        if data and isinstance(data, dict):
            if 'cct' in data:
                meta['cct'] = int(data['cct'])
            wbc = data.get('wbc')
            if isinstance(wbc, list) and len(wbc) >= 2:
                meta['wbc_r'] = float(wbc[0])
                meta['wbc_b'] = float(wbc[1])
            elif isinstance(wbc, str):
                # 如果 yaml 将其解析为字符串，尝试从字符串中提取
                match = re.search(r'\[([0-9.]+),\s*([0-9.]+)\]', wbc)
                if match:
                    meta['wbc_r'] = float(match.group(1))
                    meta['wbc_b'] = float(match.group(2))

        # 2. 如果 yaml 解析没拿到 wbc 或 cct，使用正则表达式兜底
        if 'wbc_r' not in meta:
            match = re.search(r'wbc:\s*\[([0-9.]+),\s*([0-9.]+)\]', content)
            if match:
                meta['wbc_r'] = float(match.group(1))
                meta['wbc_b'] = float(match.group(2))
                
        if 'cct' not in meta:
            match = re.search(r'cct:\s*([0-9]+)', content)
            if match:
                meta['cct'] = int(match.group(1))
                
    except Exception as e:
        print(f"  [WARNING] 解析 txt 失败 {txt_path}: {e}")
        
    return meta

def generate_meta_result(scene_name, txt_meta):
    """
    生成 meta 结果字典，结合 SCENE_METADATA 和 txt_meta
    """
    result = {}
    
    meta = SCENE_METADATA.get(scene_name, {})
    
    # 获取 gain 和 sens_ratio (来自 SCENE_METADATA)
    dcg_gain = meta.get('dcg_a_gain', 1.0)
    lofic_gain = meta.get('lofic_gain', 1.0)
    sens_ratio = meta.get('sens_ratio', 4)
    
    # 获取 cct 和 wbc (优先来自 txt_meta，其次默认值)
    cct = txt_meta.get('cct', 4000)
    wbc_r = txt_meta.get('wbc_r', 2.0)
    wbc_b = txt_meta.get('wbc_b', 2.0)
    
    print(f"  [INFO] 场景 {scene_name}: cct={cct}, wbc_r={wbc_r:.4f}, wbc_b={wbc_b:.4f}, dcg_gain={dcg_gain}, lofic_gain={lofic_gain}")

    # DCG 参数 (正常曝光帧)
    result['expotime'] = 20000000
    result['SensorAGain'] = float(dcg_gain)
    result['SensorDGain'] = 1.0
    result['sensorgain'] = float(result['SensorAGain'] * result['SensorDGain'])
    result['gain'] = result['sensorgain']
    result['isp_gain'] = 1.0
    result['iso'] = int(result['SensorAGain'] * 100)
    result['sens_ratio'] = float(sens_ratio)

    # Lofic 参数 (欠曝光帧)
    result['under_expotime'] = 20000000
    result['under_SensorAGain'] = float(lofic_gain * KEY)
    result['under_SensorDGain'] = 1.0
    result['under_sensorgain'] = float(result['under_SensorAGain'] * result['under_SensorDGain'])
    result['under_gain'] = result['under_sensorgain']
    result['under_iso'] = int(result['under_SensorAGain'] * 100)
    
    result['cct'] = int(cct)
    result['drc_gain'] = 1.0
    
    # 使用解析出的 AWB gain
    result['r_gain'] = float(wbc_r)
    result['b_gain'] = float(wbc_b)

    return result

def main():
    if not os.path.exists(UNPACK_RAW):
        print(f"错误: 找不到输入路径 {UNPACK_RAW}")
        return

    scenes = natsort.natsorted(os.listdir(UNPACK_RAW))
    print(f"找到 {len(scenes)} 个场景:")
    for scene in scenes:
        print(f"  - {scene}")

    for scene in scenes:
        scene_path = os.path.join(UNPACK_RAW, scene)
        if not os.path.isdir(scene_path):
            continue
            
        # 查找对应的 txt 文件
        txt_files = glob.glob(os.path.join(RECEIVED, scene, '*.txt'))
        
        # 如果精确匹配没找到，尝试在 RECEIVED 下进行模糊匹配（防止文件夹命名有细微差异）
        if not txt_files:
            for r_scene in os.listdir(RECEIVED):
                if scene in r_scene or r_scene in scene:
                    txt_files = glob.glob(os.path.join(RECEIVED, r_scene, '*.txt'))
                    if txt_files:
                        print(f"  [INFO] 精确匹配失败，通过模糊匹配找到 txt 文件夹: {r_scene}")
                        break

        txt_meta = {}
        if txt_files:
            txt_meta = parse_txt_meta(txt_files[0])
            print(f"  [INFO] 找到并解析 txt: {os.path.basename(txt_files[0])}")
        else:
            print(f"  [WARNING] 未在 {RECEIVED} 下找到 {scene} 对应的 txt 文件，将使用默认 cct/wbc (2.0)")

        yaml_folder = os.path.join(YAML_ROOT, scene)
        os.makedirs(yaml_folder, exist_ok=True)

        raw_files = natsort.natsorted(glob.glob(os.path.join(scene_path, '*.raw')))
        print(f"\n正在处理场景: {scene}")
        print(f"  发现 {len(raw_files)} 帧图像")
        
        # 传入 txt_meta 生成基础 meta
        base_meta = generate_meta_result(scene, txt_meta)
        
        for frame_idx, raw_file in enumerate(raw_files):
            try:
                result = base_meta.copy()

                yaml_file = os.path.join(yaml_folder, f'{str(frame_idx).zfill(3)}.yaml')
                with open(yaml_file, 'w') as fo:
                    fo.write(EXAMPLE_META) 
                    yaml.safe_dump(result, stream=fo, default_flow_style=False, sort_keys=False)
                    
            except Exception as e:
                print(f"  [ERROR] 处理文件失败 {os.path.basename(raw_file)}: {e}")
                import traceback
                traceback.print_exc()

    print("\n所有场景的 YAML 元数据文件已生成完毕！")

if __name__ == "__main__":
    main()