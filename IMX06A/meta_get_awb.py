import os
import glob
import re
import numpy as np
import natsort

# --- 配置参数 ---
ROOT = r"D:\Data\2026_06\11\HY_IMX06A_20260601"
RECEIVED = os.path.join(ROOT, "received")
UNPACK_RAW = os.path.join(ROOT, "unpack_raw")
YAML_ROOT = os.path.join(ROOT, "yamls_eachFrame")
os.makedirs(YAML_ROOT, exist_ok=True)

# RAW 图像处理相关常量
BLACK_LEVEL = 256.0  # 根据txt文件中的BlackLevel
WHITE_LEVEL = 4095.0
BAYER_PATTERN = 'RGGB'
HEIGHT = 2160
WIDTH = 3840

EXAMPLE_META = '''Black_level: 256.0
White_level: 4095.0
bayer_pattern: RGGB
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
'''

def parse_meta_txt(txt_path):
    """
    解析txt meta文件，提取每一帧的信息
    返回字典: {frame_index: {'ISO': xxx, 'Exposure_Time_0': xxx, ...}}
    """
    frames_meta = {}
    
    if not os.path.exists(txt_path):
        print(f"  警告: Meta文件不存在: {txt_path}")
        return frames_meta
    
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用正则表达式匹配所有Frame块
        frame_pattern = r'\[Frame(\d+)\](.*?)(?=\[Frame\d+\]|\Z)'
        matches = re.findall(frame_pattern, content, re.DOTALL)
        
        for frame_idx, frame_content in matches:
            frame_num = int(frame_idx)
            frame_info = {}
            
            # 提取ISO
            iso_match = re.search(r'ISO=(\d+)', frame_content)
            if iso_match:
                frame_info['ISO'] = int(iso_match.group(1))
            
            # 提取Exposure_Time_0
            exp_match = re.search(r'Exposure_Time_0=(\d+)', frame_content)
            if exp_match:
                frame_info['Exposure_Time_0'] = int(exp_match.group(1))
            
            # 提取A_Gain_0
            again_match = re.search(r'A_Gain_0=(\d+)', frame_content)
            if again_match:
                frame_info['A_Gain_0'] = int(again_match.group(1))
            
            # 提取D_Gain_0
            dgain_match = re.search(r'D_Gain_0=(\d+)', frame_content)
            if dgain_match:
                frame_info['D_Gain_0'] = int(dgain_match.group(1))
            
            # 提取ISP_D_Gain_0
            ispdgain_match = re.search(r'ISP_D_Gain_0=(\d+)', frame_content)
            if ispdgain_match:
                frame_info['ISP_D_Gain_0'] = int(ispdgain_match.group(1))
            
            frames_meta[frame_num] = frame_info
        
        print(f"  从txt文件解析到 {len(frames_meta)} 帧meta信息")
        
    except Exception as e:
        print(f"  错误: 解析txt文件失败 - {e}")
    
    return frames_meta


def get_awb_gain_from_raw(raw_file_path):
    """从raw文件计算AWB增益"""
    try:
        raw_data = np.fromfile(raw_file_path, dtype=np.uint16)
        img = raw_data.reshape(HEIGHT, WIDTH).astype(float)
        img = (img - BLACK_LEVEL) / (WHITE_LEVEL - BLACK_LEVEL)
        img = img.clip(0, 1)
        
        if BAYER_PATTERN == 'RGGB':
            sum_r = np.sum(img[0::2, 0::2])
            sum_b = np.sum(img[1::2, 1::2])
            sum_g = np.sum(img[0::2, 1::2]) + np.sum(img[1::2, 0::2])
        
        scale_r = max(1.0, sum_g / 2 / sum_r) if sum_r > 0 else 1.0
        scale_b = max(1.0, sum_g / 2 / sum_b) if sum_b > 0 else 1.0
        
        return scale_r, scale_b
    except Exception as e:
        print(f"  警告: 计算AWB增益失败 - {e}")
        return 1.0, 1.0


def extract_val(pattern, string, default=1.0):
    """从字符串中提取数值（支持3p3x这种格式）"""
    match = re.search(pattern, string, re.IGNORECASE)
    if match:
        val_str = match.group(1).replace('p', '.')
        try:
            return float(val_str)
        except:
            return default
    return default


# --- 主处理流程 ---
print("="*80)
print("开始处理RAW文件并生成YAML meta信息")
print("="*80)

# 遍历 unpack_raw 文件夹
scenes = natsort.natsorted(os.listdir(UNPACK_RAW))

for scene in scenes:
    raw_scene_dir = os.path.join(UNPACK_RAW, scene)
    if not os.path.isdir(raw_scene_dir):
        continue
    
    print(f"\n处理场景: {scene}")
    print("-" * 60)
    
    # 1. 从文件夹名提取参数
    f_again = extract_val(r"again([\dp\.]+)x", scene, 1.0)
    f_ispd = extract_val(r"ispdgain([\dp\.]+)x", scene, 1.0)
    f_drc = extract_val(r"drcgain([\dp\.]+)x", scene, 1.0)
    
    # 2. 匹配对应的 received 目录获取txt meta文件
    # 去掉数字前缀，例如 "00_6X_4_D_gain" -> "6X_4_D_gain"
    recv_scene_name = re.sub(r"^\d+__", "", scene)
    recv_scene_dir = os.path.join(RECEIVED, recv_scene_name)
    
    # 查找txt文件
    txt_files = glob.glob(os.path.join(recv_scene_dir, "*.txt"))
    
    if txt_files:
        txt_file = txt_files[0]  # 使用第一个txt文件
        print(f"  使用meta文件: {os.path.basename(txt_file)}")
        frames_meta = parse_meta_txt(txt_file)
    else:
        print(f"  警告: 在 {recv_scene_dir} 中未找到txt文件")
        frames_meta = {}
    
    # 3. 获取raw文件列表
    raw_files = natsort.natsorted(glob.glob(os.path.join(raw_scene_dir, "*.raw")))
    if not raw_files:
        print(f"  警告: 未找到RAW文件")
        continue
    
    print(f"  找到 {len(raw_files)} 个RAW文件")
    
    # 4. 创建输出目录
    out_scene_path = os.path.join(YAML_ROOT, scene)
    os.makedirs(out_scene_path, exist_ok=True)
    
    # 5. 计算AWB增益（使用第一帧）
    raw_awb_r, raw_awb_b = get_awb_gain_from_raw(raw_files[0])
    print(f"  AWB增益: R={raw_awb_r:.4f}, B={raw_awb_b:.4f}")
    
    # 6. 为每一帧生成YAML文件
    success_count = 0
    for i, raw_file in enumerate(raw_files):
        yaml_path = os.path.join(out_scene_path, f"{str(i).zfill(3)}.yaml")
        
        # 从meta信息中获取数据
        meta_info = frames_meta.get(i, {})
        
        # 计算gain和expotime
        iso = meta_info.get('ISO', 100)
        exposure_time_0 = meta_info.get('Exposure_Time_0', 0)
        
        # gain = ISO / 100
        gain = iso / 100.0
        
        # expotime = Exposure_Time_0 * 1000 (假设单位转换)
        expotime = exposure_time_0 * 1000
        
        # 获取AWB增益
        r_gain = meta_info.get('r_gain', raw_awb_r)
        b_gain = meta_info.get('b_gain', raw_awb_b)
        
        # 其他参数
        cct = 4000  # 默认值
        lux_index = 300  # 默认值
        
        # 写入YAML文件
        try:
            with open(yaml_path, "w") as fo:
                fo.write(EXAMPLE_META)
                fo.write(f"gain: {gain:.4f}\n")
                fo.write(f"SensorAGain: {gain:.4f}\n")
                fo.write(f"sensorgain: {gain:.4f}\n")
                fo.write(f"SensorDGain: 1.0000\n")
                fo.write(f"iso: {iso}\n")
                fo.write(f"expotime: {expotime}\n")
                fo.write(f"isp_gain: 1.0000\n")
                fo.write(f"cct: {cct}\n")
                fo.write(f"r_gain: {r_gain:.4f}\n")
                fo.write(f"b_gain: {b_gain:.4f}\n")
                fo.write(f"drc_gain: 1.0000\n")
                fo.write(f"lux_index: {lux_index}\n")
                fo.write(f"luxid: {lux_index}\n")
            
            success_count += 1
            
            # 显示前3帧和最后1帧的详细信息
            if i < 3 or i == len(raw_files) - 1:
                print(f"    Frame {i:03d}: ISO={iso}, ExpTime={exposure_time_0}, "
                      f"gain={gain:.4f}, expotime={expotime}")
            elif i == 3:
                print(f"    ... (省略中间帧)")
        
        except Exception as e:
            print(f"    错误: 写入YAML文件失败 - {e}")
    
    print(f"\n[OK] {scene} -> 成功生成 {success_count}/{len(raw_files)} 个YAML文件")
    print(f"     参数: again={f_again}, ispd={f_ispd}, drc={f_drc}")

print("\n" + "="*80)
print("处理完成!")
print("="*80)