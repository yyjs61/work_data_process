import os, glob, yaml, natsort, json, re

# ROOT = '/home/user/afs_data/LeeSin_Xie/Quad_dag_20260409/'
ROOT = r"D:\Data\20260416\quad_potraitraw_for_yw-2026-04-16\quad_potraitraw_for_yw/"

UNPACK_RAW = os.path.join(ROOT, 'unpack_raw')
RECEIVED_ROOT = os.path.join(ROOT, 'received')  # received 目录路径

EXAMPLE_META = '''
Black_level: 64.0
White_level: 4095.0
height: 2304.0
width: 4096.0
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
bayer_pattern: BGGR
'''

def load_forgiving_json(file_path):
    """自动修复非标准 JSON（处理 None、行内注释、尾部逗号）"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # 1. Python None -> JSON null
    content = content.replace('None', 'null')
    # 2. 移除括号内的中文注释（兼容中英文括号）
    content = re.sub(r'\s*\([^)]*\)', '', content)
    content = re.sub(r'\s*（[^）]*）', '', content)
    # 3. 清理因删除注释可能残留的尾部逗号（如 "data": 1.0, } -> "data": 1.0 }）
    content = re.sub(r',\s*([}\]])', r'\1', content)
    return json.loads(content)

def generate_frame_meta(frame_idx, analog_gain=1.0):
    """
    生成单帧元数据
    :param frame_idx: 帧索引
    :param analog_gain: 传感器模拟增益，用于计算 ISO
    :return: 元数据字典
    """
    result = {}
    
    # 1. 根据 analog_gain 计算 ISO
    iso = analog_gain * 100.0
    gain = analog_gain
    
    result['iso'] = iso
    result['SensorAGain'] = gain
    result['sensorgain'] = gain
    result['gain'] = gain
    result['SensorDGain'] = 1.0
    result['expotime'] = 20000000  # 曝光时间，单位 ns

    # 设置默认白平衡增益，如果 JSON 读取失败或不存在，将使用这些值
    result['r_gain'] = 2.056
    result['b_gain'] = 2.168
    result['lux_index'] = 443.0
    result['luxid'] = 443.0
    result['cct'] = 4000
    result['isp_gain'] = 1.0
    result['drc_gain'] = 1.0

    return result

# 主处理流程
scenes = natsort.natsorted(os.listdir(UNPACK_RAW))

for scene in scenes:
    scene_path = os.path.join(UNPACK_RAW, scene)
    yaml_folder = os.path.join(ROOT, 'yamls_eachFrame', scene)
    os.makedirs(yaml_folder, exist_ok=True)
    
    # 1. 尝试读取对应的 JSON 文件
    # 移除文件夹名的 "00__" 前缀来获取 JSON 文件名
    json_scene_name = scene
    # if scene.startswith("00__"):
    json_scene_name = scene[4:]  # 移除前 4 个字符 "00__"
    
    json_file_path = os.path.join(RECEIVED_ROOT, f"{json_scene_name}.json")
    
    # 初始化从 JSON 读取的值
    r_gain_val = None
    b_gain_val = None
    analog_gain_val = 1.0  # 默认模拟增益为 1.0
    
    if os.path.exists(json_file_path):
        try:
            # 使用兼容函数替代原生 json.load
            json_data = load_forgiving_json(json_file_path)
            
            # 2. 提取 wb_gain -> data -> [rgain, gain, bgain]
            if 'wb_gain' in json_data and 'data' in json_data['wb_gain']:
                wb_data = json_data['wb_gain']['data']
                if len(wb_data) >= 3:
                    r_gain_val = wb_data[0]  # rgain
                    b_gain_val = wb_data[2]  # bgain
                    print(f"[Info] Loaded WB gains for {scene}: R={r_gain_val}, B={b_gain_val}")
                else:
                    print(f"[Warn] wb_gain data length < 3 in {json_file_path}")
            else:
                print(f"[Warn] 'wb_gain' key not found in {json_file_path}")
            
            # 3. 提取 analog_gain -> data
            if 'analog_gain' in json_data and 'data' in json_data['analog_gain']:
                analog_gain_val = json_data['analog_gain']['data']
                print(f"[Info] Loaded analog_gain for {scene}: {analog_gain_val} (ISO={analog_gain_val * 100})")
            else:
                print(f"[Warn] 'analog_gain' key not found in {json_file_path}, using default 1.0")
                
        except Exception as e:
            print(f"[Error] Failed to parse {json_file_path}: {e}")
    else:
        print(f"[Warn] JSON file not found: {json_file_path}, using default values.")
    
    # 4. 处理该场景下的所有 RAW 文件
    raw_files = natsort.natsorted(glob.glob(os.path.join(scene_path, '*.raw')))
    
    for frame_idx, raw_file in enumerate(raw_files):
        # 5. 生成元数据，传入 analog_gain
        result = generate_frame_meta(frame_idx, analog_gain=analog_gain_val)
        
        # 6. 如果从 JSON 读取到了有效的 WB 值，则覆盖 result 中的默认值
        if r_gain_val is not None:
            result['r_gain'] = r_gain_val
        if b_gain_val is not None:
            result['b_gain'] = b_gain_val 

        # 7. 写入 YAML 文件
        yaml_file = os.path.join(yaml_folder, f'{str(frame_idx).zfill(3)}.yaml')
        with open(yaml_file, 'w') as fo:
            fo.write(EXAMPLE_META)
            yaml.safe_dump(result, stream=fo, default_flow_style=False)
    
    print(f"[Done] Scene {scene}: {len(raw_files)} frames processed.\n")

print("=" * 60)
print("全部场景处理完成")
print("=" * 60)