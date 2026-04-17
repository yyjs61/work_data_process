import glob
import os
import re
import numpy as np

def extract_req_number(filename):
    """从文件名中提取req[]中的数字"""
    match = re.search(r'req\[(\d+)\]', filename)
    return int(match.group(1)) if match else None

def parse_txt_meta(txt_file_path):
    """解析txt文件，提取元数据"""
    result = {}
    
    with open(txt_file_path, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('====='):
            continue
        
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            try:
                if '.' in value:
                    result[key] = float(value)
                else:
                    result[key] = int(value)
            except ValueError:
                result[key] = value
    
    return result

def get_awb_gain_from_raw(raw_file_path, bayer_pattern='BGGR', width=4096, height=3072, wp=16368, bp=1024):
    """从raw文件计算AWB增益"""
    try:
        img = np.fromfile(raw_file_path, dtype=np.uint16).reshape([height, width]).astype(float)
        img = (img - bp) / (wp - bp)
        img = img.clip(0, 1)
        
        # BGGR pattern
        c1 = img[1::2, 1::2]
        c2 = img[0::2, 0::2]
        c3 = img[0::2, 1::2]
        c4 = img[1::2, 0::2]
        c1[c1 > (0.4 * wp)/wp] = 0
        c2[c2 > (0.4 * wp)/wp] = 0
        c3[c3 > (0.95 * wp)/wp] = 0
        c4[c4 > (0.95 * wp)/wp] = 0
        sum_r = np.sum(c1)
        sum_b = np.sum(c2)
        sum_g = np.sum(c3) + np.sum(c4)
        
        if sum_r > 0:
            scale_r = max(1, sum_g/2/sum_r)
        else:
            scale_r = 1.0
            
        if sum_b > 0:
            scale_b = max(1, sum_g/2/sum_b)
        else:
            scale_b = 1.0
            
        return scale_r, scale_b
    except Exception as e:
        print(f"  计算AWB增益失败: {e}")
        return 1.0, 1.0

def map_scene_name(unpack_scene_name):
    """将unpack_raw中的场景名映射到received中的场景名"""
    match = re.match(r'^\d+__', unpack_scene_name)
    if match:
        return unpack_scene_name[match.end():]
    return unpack_scene_name

def write_yaml_file(filepath, data):
    """手动写入yaml文件，保持ccm_matrix格式"""
    with open(filepath, 'w') as f:
        f.write(f"bayer_pattern: {data['bayer_pattern']}\n")
        f.write(f"Black_level: {data['Black_level']}\n")
        f.write(f"White_level: {data['White_level']}\n")
        f.write(f"under_Black_level: {data['under_Black_level']}\n")
        f.write(f"under_White_level: {data['under_White_level']}\n")
        f.write("ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]\n")
        f.write(f"\n")

        f.write(f"lux_index: {data['lux_index']}\n")
        f.write(f"luxid: {data['luxid']}\n")
        f.write(f"isp_gain: {data['isp_gain']}\n")
        f.write(f"\n")

        f.write(f"expotime: {data['expotime']}\n")
        f.write(f"sensorgain: {data['sensorgain']}\n")
        f.write(f"gain: {data['gain']}\n")
        f.write(f"iso: {data['iso']}\n")
        f.write(f"\n")

        f.write(f"under_expotime: {data['under_expotime']}\n")
        f.write(f"under_sensorgain: {data['under_sensorgain']}\n")
        f.write(f"under_gain: {data['under_gain']}\n")
        f.write(f"under_iso: {data['under_iso']}\n")
        f.write(f"\n")

        f.write(f"r_gain: {data['r_gain']}\n")
        f.write(f"b_gain: {data['b_gain']}\n")
        f.write(f"cct: {data['cct']}\n")
        f.write(f"\n")




def main():
    # ROOT = r'C:\Users\admin.DESKTOP-QNCO006\Desktop\Data\Noise_lofic\sensor_20/'
    ROOT = r'C:\Users\admin.DESKTOP-QNCO006\Desktop\Data\OV50X\OV50X_DCGandLOFIC_20260410__lab_ipad/'
    RECEIVED = ROOT + 'received/'
    UNPACK_RAW = ROOT + 'unpack_raw/'
    YAML_OUTPUT = ROOT + 'yamls_eachFrame/'
    
    BAYER_PATTERN = 'BGGR'
    WIDTH = 4096
    HEIGHT = 3072
    WP = 16383
    BP = 256
    UNDER_BP = 256
    UNDER_WP = 4095
    
    os.makedirs(YAML_OUTPUT, exist_ok=True)
    
    unpack_scenes = sorted([d for d in os.listdir(UNPACK_RAW) 
                            if os.path.isdir(os.path.join(UNPACK_RAW, d))])
    
    print(f"找到 {len(unpack_scenes)} 个unpack_raw场景\n")
    
    for unpack_scene in unpack_scenes:
        unpack_scene_path = os.path.join(UNPACK_RAW, unpack_scene)
        received_scene = map_scene_name(unpack_scene)
        received_scene_path = os.path.join(RECEIVED, received_scene)
        
        print(f"处理场景: {unpack_scene} -> {received_scene}")
        
        if not os.path.exists(received_scene_path):
            print(f"  ✗ received场景不存在，跳过\n")
            continue
        
        raw_files = sorted(glob.glob(os.path.join(unpack_scene_path, '*.raw')))
        
        if not raw_files:
            print(f"  ✗ 没有找到raw文件\n")
            continue
        
        print(f"  找到 {len(raw_files)} 个raw文件")
        
        # 预先获取所有txt文件并建立映射
        all_txt_files = glob.glob(os.path.join(received_scene_path, '*.txt'))
        txt_mapping = {}
        for txt_file in all_txt_files:
            txt_filename = os.path.basename(txt_file)
            req = extract_req_number(txt_filename)
            if req is not None:
                txt_mapping[req] = txt_file
        
        print(f"  找到 {len(txt_mapping)} 个txt文件映射")
        
        yaml_count = 0
        missing_txt_count = 0
        
        # 按文件名排序处理
        for idx, raw_file in enumerate(raw_files):
            filename = os.path.basename(raw_file)
            req_num = extract_req_number(filename)
            
            if req_num is None:
                print(f"    警告: 无法提取req值 - {filename}")
                continue
            
            # 直接从映射中查找
            if req_num not in txt_mapping:
                print(f"    跳过: req[{req_num}] 没有找到txt文件 - {filename}")
                missing_txt_count += 1
                continue
            
            txt_file = txt_mapping[req_num]
            
            # 解析txt文件
            meta_data = parse_txt_meta(txt_file)
            
            # 创建yaml文件名（按序号）
            yaml_filename = f"{idx:03d}.yaml"
            scene_yaml_dir = os.path.join(YAML_OUTPUT, unpack_scene)
            os.makedirs(scene_yaml_dir, exist_ok=True)
            yaml_path = os.path.join(scene_yaml_dir, yaml_filename)
            
            # 计算AWB增益
            r_gain, b_gain = get_awb_gain_from_raw(raw_file, BAYER_PATTERN, WIDTH, HEIGHT, WP, BP)
            
            # 准备数据
            yaml_data = {
                'Black_level': BP,
                'White_level': WP,
                'under_Black_level': UNDER_BP,
                'under_White_level': UNDER_WP,
                'bayer_pattern': BAYER_PATTERN,
                'lux_index': meta_data.get('lux', 300.0),
                'luxid': meta_data.get('lux', 300.0),
                'cct': meta_data.get('awbCt', 4000.0),
                'expotime': meta_data.get('expTime(ns)', 0.0),
                'iso': meta_data.get('iso', 100.0),
                # 'gain': meta_data.get('totalGain', 1.0),
                'gain': meta_data.get('iso', 100.0) / 100,

                'sensorgain': meta_data.get('sensorGain', 1.0),
                'isp_gain': meta_data.get('ispGain', 1.0),
                'r_gain': float(r_gain),
                'b_gain': float(b_gain),
                'under_expotime': meta_data.get('expTime(ns)', 0.0),
                'under_sensorgain': meta_data.get('sensorGain', 1.0),
                # 'under_gain': meta_data.get('totalGain', 1.0),
                'under_gain': meta_data.get('iso', 100.0) / 100,
                'under_iso': meta_data.get('iso', 100.0),
            }
            
            # 写入yaml文件
            write_yaml_file(yaml_path, yaml_data)
            
            yaml_count += 1
            if yaml_count % 10 == 0:
                print(f"    已生成 {yaml_count} 个yaml...")
        
        print(f"  完成: 生成 {yaml_count} 个yaml, 跳过 {missing_txt_count} 个\n")

if __name__ == '__main__':
    main()