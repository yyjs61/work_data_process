import os
import glob
import yaml
import natsort
import json
import re
import numpy as np

ROOT = r"D:\Data\DJI_OV50X\20260509\DJI_8xx_20260509"
UNPACK_RAW = os.path.join(ROOT, 'unpack_raw')
RECEIVED_ROOT = os.path.join(ROOT, 'received')

EXAMPLE_META = '''
Black_level: 64.0
White_level: 4095.0
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
bayer_pattern: RGGB
'''

def parse_resolution_from_filename(filename):
    """
    从raw文件名中解析分辨率
    例如: 000_video_braw_dump__11772_4096x2304_400890400.raw -> (4096, 2304)
    """
    # 匹配 WxH 模式，如 4096x2304
    match = re.search(r'(\d{3,4})[xX](\d{3,4})', os.path.basename(filename))
    if match:
        width = int(match.group(1))
        height = int(match.group(2))
        return width, height
    return None, None

def parse_readme(readme_path):
    """
    解析readme.txt文件，提取iso、shutter和分辨率参数
    """
    params = {
        'iso': 100,
        'shutter': 10.0,  # 单位ms
        'width': None,
        'height': None
    }
    
    if not os.path.exists(readme_path):
        print(f"  [Warn] readme.txt not found: {readme_path}")
        return params
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 解析iso（支持中文冒号和英文冒号）
        iso_match = re.search(r'iso[：:]\s*(\d+)', content, re.IGNORECASE)
        if iso_match:
            params['iso'] = int(iso_match.group(1))
            
        # 解析shutter（支持中文冒号和英文冒号）
        shutter_match = re.search(r'shutter[：:]\s*([\d.]+)\s*ms', content, re.IGNORECASE)
        if shutter_match:
            params['shutter'] = float(shutter_match.group(1))
            
        # 解析分辨率（支持 * 或 x 或 X 作为分隔符）
        res_match = re.search(r'分辨率[：:]\s*(\d+)\s*[\*xX]\s*(\d+)', content)
        if res_match:
            params['width'] = int(res_match.group(1))
            params['height'] = int(res_match.group(2))
            
        print(f"  [Info] Parsed readme.txt: ISO={params['iso']}, Shutter={params['shutter']}ms, "
              f"Resolution={params['width']}x{params['height']}")
              
    except Exception as e:
        print(f"  [Error] Failed to parse readme.txt: {e}")
    
    return params


    """从raw文件计算AWB增益（使用4x4 HEX解包）"""
    try:
        raw_data = np.fromfile(raw_file_path, dtype=np.uint16)
        expected_size = width * height
        
        if len(raw_data) != expected_size:
            print(f"  [Warn] Raw size mismatch: {len(raw_data)} vs {expected_size}")
            return 1.0, 1.0
        
        img = raw_data.reshape([height, width]).astype(np.float32)
        img = (img - bp) / (wp - bp)
        img = np.clip(img, 0, 1)
        
        # 使用 4x4 HEX 模式提取通道
        # 假设标准 HEX 排列：
        # R G G R
        # G B B G
        # G B B G
        # R G G R
        # 提取每个 4x4 块中的 R、G、B 位置
        
        # R 在 (0,0), (0,3), (3,0), (3,3) 等位置
        r_channel = np.concatenate([
            img[0::4, 0::4],  # (0,0)
            img[0::4, 3::4],  # (0,3)
            img[3::4, 0::4],  # (3,0)
            img[3::4, 3::4]   # (3,3)
        ])
        
        # G 在 (0,1), (0,2), (1,0), (1,3), (2,0), (2,3), (3,1), (3,2) 等位置
        g_channel = np.concatenate([
            img[0::4, 1::4], img[0::4, 2::4],
            img[1::4, 0::4], img[1::4, 3::4],
            img[2::4, 0::4], img[2::4, 3::4],
            img[3::4, 1::4], img[3::4, 2::4]
        ])
        
        # B 在 (1,1), (1,2), (2,1), (2,2) 等位置
        b_channel = np.concatenate([
            img[1::4, 1::4], img[1::4, 2::4],
            img[2::4, 1::4], img[2::4, 2::4]
        ])
        
        # 计算各通道平均值
        avg_r_raw = np.mean(r_channel)
        avg_g_raw = np.mean(g_channel)
        avg_b_raw = np.mean(b_channel)
        
        print(f"  [Debug] 原始通道均值 -> R: {avg_r_raw:.4f}, G: {avg_g_raw:.4f}, B: {avg_b_raw:.4f}")
        
        # 过滤过饱和像素
        r_mask = r_channel < 0.4
        b_mask = b_channel < 0.4
        g_mask = g_channel < 0.95
        
        sum_r = np.sum(r_channel[r_mask])
        sum_b = np.sum(b_channel[b_mask])
        sum_g = np.sum(g_channel[g_mask])
        
        count_r = np.sum(r_mask)
        count_b = np.sum(b_mask)
        count_g = np.sum(g_mask)
        
        avg_r = sum_r / count_r if count_r > 0 else 0
        avg_b = sum_b / count_b if count_b > 0 else 0
        avg_g = sum_g / count_g if count_g > 0 else 0
        
        print(f"  [Debug] 过滤后均值 -> R: {avg_r:.4f}, G: {avg_g:.4f}, B: {avg_b:.4f}")
        print(f"  [Debug] 有效像素 -> R: {count_r}, G: {count_g}, B: {count_b}")
        
        # 计算增益
        if avg_r > 0:
            scale_r = max(1.0, avg_g / avg_r)
        else:
            scale_r = 1.0
            
        if avg_b > 0:
            scale_b = max(1.0, avg_g / avg_b)
        else:
            scale_b = 1.0
        
        print(f"  [Debug] 计算增益 -> R: {scale_r:.4f}, B: {scale_b:.4f}")
        
        return float(scale_r), float(scale_b)
        
    except Exception as e:
        print(f"  [Error] AWB计算失败: {e}")
        import traceback
        traceback.print_exc()
        return 1.0, 1.0

def get_awb_gain_from_raw(raw_file_path, bayer_pattern='RGGB', width=4096, height=2304, wp=4095, bp=64):
    """
    从 Quad Bayer Raw 计算 AWB 增益
    使用与 QuadBayer2CHW 完全一致的通道分离逻辑，确保 R/G/B 统计准确
    """
    try:
        raw_data = np.fromfile(raw_file_path, dtype=np.uint16)
        expected_size = width * height
        if len(raw_data) != expected_size:
            print(f"  [Warn] Raw size mismatch: {len(raw_data)} vs {expected_size}")
            return 1.0, 1.0

        # 1. Reshape & 归一化
        img = raw_data.reshape([height, width]).astype(np.float32)
        img = (img - bp) / (wp - bp)
        img = np.clip(img, 0, 1)

        # 2. QuadBayer2CHW 通道分离逻辑 (与你的可视化脚本完全一致)
        H, W = img.shape
        chw = np.zeros([4, H//2, W//2], dtype=np.float32)
        SHIFT = {0: {'Y': 0, 'X': 0}, 1: {'Y': 0, 'X': 2}, 
                 2: {'Y': 2, 'X': 0}, 3: {'Y': 2, 'X': 2}}
        for i, c in enumerate(chw):
            c[0::2, 0::2] = img[SHIFT[i]['Y'] + 0::4, SHIFT[i]['X'] + 0::4]
            c[0::2, 1::2] = img[SHIFT[i]['Y'] + 0::4, SHIFT[i]['X'] + 1::4]
            c[1::2, 0::2] = img[SHIFT[i]['Y'] + 1::4, SHIFT[i]['X'] + 0::4]
            c[1::2, 1::2] = img[SHIFT[i]['Y'] + 1::4, SHIFT[i]['X'] + 1::4]

        c0, c1, c2, c3 = chw

        # 3. 根据 Pattern 映射 R, G1, G2, B (严格对齐 CHW2RGB)
        if bayer_pattern.upper() == 'RGGB':
            r_ch, g1_ch, g2_ch, b_ch = c0, c1, c2, c3
        elif bayer_pattern.upper() == 'BGGR':
            b_ch, g1_ch, g2_ch, r_ch = c0, c1, c2, c3
        elif bayer_pattern.upper() == 'GRBG':
            g1_ch, r_ch, b_ch, g2_ch = c0, c1, c2, c3
        elif bayer_pattern.upper() == 'GBRG':
            g1_ch, b_ch, r_ch, g2_ch = c0, c1, c2, c3
        else:
            print(f"  [Error] Unknown bayer pattern: {bayer_pattern}")
            return 1.0, 1.0

        # 4. 计算通道均值 (Quad 已做 2x2 合并，直接统计即可)
        avg_r = np.mean(r_ch)
        avg_g = (np.mean(g1_ch) + np.mean(g2_ch)) / 2.0
        avg_b = np.mean(b_ch)
        print(f"  [Debug] Quad通道均值 -> R: {avg_r:.4f}, G: {avg_g:.4f}, B: {avg_b:.4f}")

        # 5. 过滤过饱和/过暗像素
        r_mask = r_ch < 0.4
        b_mask = b_ch < 0.4
        g1_mask = g1_ch < 0.95
        g2_mask = g2_ch < 0.95

        sum_r = np.sum(r_ch[r_mask])
        sum_b = np.sum(b_ch[b_mask])
        sum_g = np.sum(g1_ch[g1_mask]) + np.sum(g2_ch[g2_mask])
        count_r = np.sum(r_mask)
        count_b = np.sum(b_mask)
        count_g = np.sum(g1_mask) + np.sum(g2_mask)

        avg_r_safe = sum_r / count_r if count_r > 0 else 0
        avg_b_safe = sum_b / count_b if count_b > 0 else 0
        avg_g_safe = sum_g / count_g if count_g > 0 else 0

        # 6. 计算 AWB 增益 (以 G 为基准)
        scale_r = max(1.0, avg_g_safe / avg_r_safe) if avg_r_safe > 0 else 1.0
        scale_b = max(1.0, avg_g_safe / avg_b_safe) if avg_b_safe > 0 else 1.0

        print(f"  [Debug] 计算增益 -> R: {scale_r:.4f}, B: {scale_b:.4f}")
        return float(scale_r), float(scale_b)

    except Exception as e:
        print(f"  [Error] AWB计算失败: {e}")
        import traceback
        traceback.print_exc()
        return 1.0, 1.0


def get_awb_gain(file, BAYER_PATTERN = "BGGR", WP = 4095, BP = 64, width=4096, height=2304):
    # img = np.fromfile(file,dtype=np.uint16).reshape([H,W]).astype(float)
    img = quad_bayer_to_raw(file, width, height)
    img = (img - BP) / (WP - BP)
    img = img.clip(0, 1)
    if BAYER_PATTERN == 'RGGB':
        sum_r = np.sum(img[0::2,0::2])
        sum_b = np.sum(img[1::2,1::2])
        sum_g = np.sum(img[0::2,1::2]) + np.sum(img[1::2,0::2])

        scale_r = max(1, sum_g/2/sum_r) 
        scale_b = max(1, sum_g/2/sum_b)
    elif BAYER_PATTERN == 'GBRG':
        sum_r = np.sum(img[1::2,0::2])
        sum_b = np.sum(img[0::2,1::2])
        sum_g = np.sum(img[0::2,0::2]) + np.sum(img[1::2,1::2])

        scale_r = max(1, sum_g/2/sum_r)
        scale_b = max(1, sum_g/2/sum_b)      

    elif BAYER_PATTERN == 'GRBG':
        sum_r = np.sum(img[0::2,1::2])
        sum_b = np.sum(img[1::2,0::2])
        sum_g = np.sum(img[0::2,0::2]) + np.sum(img[1::2,1::2])

        scale_r = max(1, sum_g/2/sum_r)
        scale_b = max(1, sum_g/2/sum_b)


    elif BAYER_PATTERN == 'BGGR':
        sum_r = np.sum(img[1::2,1::2])
        sum_b = np.sum(img[0::2,0::2])
        sum_g = np.sum(img[0::2,1::2]) + np.sum(img[1::2,0::2])

        scale_r = max(1, sum_g/2/sum_r)
        scale_b = max(1, sum_g/2/sum_b)
    # print(scale_r, scale_b)
    return scale_r, scale_b

def quad_bayer_to_raw(quad_bayer, W=4096, H=2304):
    quad_bayer = np.fromfile(quad_bayer,dtype=np.uint16).reshape([H,W]).astype(float)
    '''
        G R  g1 g2    
        B G  g3 g4
    '''
    raw = np.zeros([quad_bayer.shape[0]//2,quad_bayer.shape[1]//2],dtype=np.uint16).astype(float)

    g1_1 = quad_bayer[::4,::4]
    g1_2 = quad_bayer[::4,1::4]
    g1_3 = quad_bayer[1::4,::4]
    g1_4 = quad_bayer[1::4,1::4]
    raw[::2,::2] = (g1_1 + g1_2 + g1_3 + g1_4)/4

    r1 = quad_bayer[::4,2::4]
    r2 = quad_bayer[::4,3::4]
    r3 = quad_bayer[1::4,2::4]
    r4 = quad_bayer[1::4,3::4]
    raw[::2,1::2] = (r1 + r2 + r3 + r4)/4

    b1 = quad_bayer[2::4,::4]
    b2 = quad_bayer[2::4,1::4]
    b3 = quad_bayer[3::4,::4]
    b4 = quad_bayer[3::4,1::4]
    raw[1::2,::2] = (b1 + b2 + b3 + b4)/4

    g2_1 = quad_bayer[2::4,2::4]
    g2_2 = quad_bayer[2::4,3::4]
    g2_3 = quad_bayer[3::4,2::4]
    g2_4 = quad_bayer[3::4,3::4]
    raw[1::2,1::2] = (g2_1 + g2_2 + g2_3 + g2_4)/4

    return raw.astype(np.uint16)

def remove_prefix(name):
    """移除递增序号前缀，如 '00__afternoon_sence' -> 'afternoon_sence'"""
    match = re.match(r'^\d+__(.+)$', name)
    if match:
        return match.group(1)
    return name

def generate_frame_meta(frame_idx, iso=100, shutter=10.0, r_gain=1.0, b_gain=1.0, width=4096, height=2304):
    """
    生成单帧元数据
    """
    result = {}
    
    # 计算analog_gain
    analog_gain = iso / 100.0
    
    # 计算曝光时间（单位ns）
    expotime = int(shutter * 1000000)  # ms -> ns
    
    result['iso'] = iso
    result['SensorAGain'] = analog_gain
    result['sensorgain'] = analog_gain
    result['gain'] = analog_gain
    result['SensorDGain'] = 1.0
    result['expotime'] = expotime
    
    # 白平衡增益
    result['r_gain'] = r_gain
    result['b_gain'] = b_gain
    
    # 其他参数
    result['lux_index'] = 443.0
    result['luxid'] = 443.0
    result['cct'] = 4000
    result['isp_gain'] = 1.0
    result['drc_gain'] = 1.0
    
    # 更新EXAMPLE_META中的分辨率
    meta_header = f'''
Black_level: 64.0
White_level: 4095.0
height: {float(height)}.0
width: {float(width)}.0
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
bayer_pattern: RGGB
'''

    return meta_header, result

def main():
    print("=" * 60)
    print("开始处理场景...")
    print("=" * 60)
    
    # 获取所有场景文件夹（unpack_raw下带前缀的场景名）
    scenes = natsort.natsorted(os.listdir(UNPACK_RAW))
    
    for scene in scenes:
        scene_path = os.path.join(UNPACK_RAW, scene)
        
        if not os.path.isdir(scene_path):
            continue
        
        # 移除前缀得到received下的场景名
        received_scene_name = remove_prefix(scene)
        
        # 创建yaml输出文件夹
        yaml_folder = os.path.join(ROOT, 'yamls_eachFrame', scene)
        os.makedirs(yaml_folder, exist_ok=True)
        
        print(f"\n[处理] 场景: {scene} -> {received_scene_name}")
        
        # 1. 读取received下对应场景的readme.txt
        readme_path = os.path.join(RECEIVED_ROOT, received_scene_name, 'readme.txt')
        params = parse_readme(readme_path)
        
        iso = min(params['iso'], 800)
        shutter = params['shutter']
        width_from_readme = params['width']
        height_from_readme = params['height']
        
        # 2. 获取raw文件列表（unpack_raw下带前缀的raw文件）
        raw_files = natsort.natsorted(glob.glob(os.path.join(scene_path, '*.raw')))
        
        if not raw_files:
            print(f"  [Warn] 没有找到RAW文件")
            continue
        
        # 3. 确定分辨率：优先使用readme.txt，否则从raw文件名解析
        width = width_from_readme
        height = height_from_readme
        
        if width is None or height is None:
            # 从第一个raw文件名解析分辨率
            width_from_file, height_from_file = parse_resolution_from_filename(raw_files[0])
            if width_from_file and height_from_file:
                width = width_from_file
                height = height_from_file
                print(f"  [Info] 从raw文件名解析分辨率: {width}x{height}")
            else:
                # 使用默认值
                width = 4096
                height = 2304
                print(f"  [Warn] 无法解析分辨率，使用默认值: {width}x{height}")
        else:
            print(f"  [Info] 从readme.txt获取分辨率: {width}x{height}")
        
        # 4. 使用第一帧raw文件计算AWB增益
        first_raw = raw_files[0]
        print(f"  [Info] 使用第一帧计算AWB增益: {os.path.basename(first_raw)}")
        r_gain, b_gain = get_awb_gain_from_raw(
            first_raw, 
            bayer_pattern='RGGB',
            width=width,
            height=height,
            wp=4095,  # White level
            bp=64     # Black level
        )
        # r_gain, b_gain = get_awb_gain(first_raw, width=width, height=height)

        print(f"  [Info] 计算得到的AWB增益: R={r_gain:.4f}, B={b_gain:.4f}")

        # 5. 处理每一帧
        for frame_idx, raw_file in enumerate(raw_files):
            # 生成元数据
            meta_header, result = generate_frame_meta(
                frame_idx=frame_idx,
                iso=iso,
                shutter=shutter,
                r_gain=r_gain,
                b_gain=b_gain,
                width=width,
                height=height
            )
            
            # 写入YAML文件
            yaml_file = os.path.join(yaml_folder, f'{str(frame_idx).zfill(3)}.yaml')
            with open(yaml_file, 'w', encoding='utf-8') as fo:
                fo.write(meta_header)
                yaml.safe_dump(result, stream=fo, default_flow_style=False)
        
        print(f"  [Done] 场景 {scene}: {len(raw_files)} 帧处理完成")
    
    print("\n" + "=" * 60)
    print("全部场景处理完成")
    print("=" * 60)

if __name__ == "__main__":
    main()