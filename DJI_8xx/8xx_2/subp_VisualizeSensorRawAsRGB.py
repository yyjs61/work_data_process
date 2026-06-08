import cv2, yaml, glob, os, sys, numpy as np, re

# 备用路径（注释掉）
# ROOT = '/home/user/afs_data/LeeSin_Xie/quadraw_for_yw_20260408/'
# ROOT = '/home/user/afs_data/LeeSin_Xie/data/TestData/'
# ROOT = r"D:\Data\20260416\quad_potraitraw_for_yw-2026-04-16\quad_potraitraw_for_yw/"
# ROOT = r"D:\Data\DJI_OV50X\20260422\flower_portrait_20260422-2026-04-22\Quad_dag_20260422/"
# ROOT = r"D:\Data\DJI_OV50X\20260506\v2_data_20260506-2026-05-06\v2_data_20260506/"
ROOT = r"D:\Data\DJI_OV50X\20260509\Quad_dag_20260509/"

UNPACK_RAW = ROOT + 'unpack_raw/'
YAML_DATA = ROOT + 'yamls_eachFrame/'
RECEIVED_ROOT = ROOT + 'received/'  # 添加received目录路径

# 默认参数
DEFAULT_H = 2304
DEFAULT_W = 4096
BAYER_PATTERN = 'RGGB'

# 位深参数
WP = 4095   # 12bit white level
BP = 64     # 12bit black level
# BP = 256     # 12bit black level

OUTPUT_DIR = 'jpg'
OUTPUT_TYPE = 'jpg'
PSEUDO_ISP_GAIN = 1
AWB_R_GAIN = 2.0
AWB_B_GAIN = 1.8
GAMMA = 2.8

DEMOSAIC_DICT = {
    'RGGB': cv2.COLOR_BAYER_BG2BGR_EA,
    'GRBG': cv2.COLOR_BAYER_GB2BGR_EA,
    'GBRG': cv2.COLOR_BAYER_GR2BGR_EA,
    'BGGR': cv2.COLOR_BAYER_RG2BGR_EA
}

def parse_resolution_from_readme(readme_path):
    """
    从readme.txt中解析分辨率
    例如: 分辨率：3968*2240 -> (3968, 2240)
    """
    if not os.path.exists(readme_path):
        return None, None
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配分辨率，支持 * x X 作为分隔符
        res_match = re.search(r'分辨率[：:]\s*(\d+)\s*[\*xX]\s*(\d+)', content)
        if res_match:
            width = int(res_match.group(1))
            height = int(res_match.group(2))
            print(f"  [Info] 从readme.txt获取分辨率: {width}x{height}")
            return width, height
    except Exception as e:
        print(f"  [Warn] 解析readme.txt失败: {e}")
    
    return None, None

def parse_resolution_from_filename(filename):
    """
    从raw文件名中解析分辨率
    例如: 000_video_braw_dump__11772_4096x2304_400890400.raw -> (4096, 2304)
    """
    # 匹配 WxH 模式，如 4096x2304 或 4096X2304
    match = re.search(r'(\d{3,4})[xX](\d{3,4})', os.path.basename(filename))
    if match:
        width = int(match.group(1))
        height = int(match.group(2))
        print(f"  [Info] 从文件名获取分辨率: {width}x{height}")
        return width, height
    return None, None

def remove_prefix(name):
    """移除递增序号前缀，如 '00__afternoon_sence' -> 'afternoon_sence'"""
    match = re.match(r'^\d+__(.+)$', name)
    if match:
        return match.group(1)
    return name

def HEX2CHW(quad_bayer):
    assert len(quad_bayer.shape) == 2
    H, W = quad_bayer.shape[0], quad_bayer.shape[1]
    chw = np.zeros([4, H//2, W//2], dtype=quad_bayer.dtype)
    SHIFT = {    
        0: {'Y': 0, 'X': 0},    
        1: {'Y': 0, 'X': 4},    
        2: {'Y': 4, 'X': 0},    
        3: {'Y': 4, 'X': 4},   
    }
    for i, c in enumerate(chw):
        c[0::4, 0::4] = quad_bayer[SHIFT[i]['Y'] + 0::8, SHIFT[i]['X'] + 0::8]
        c[0::4, 1::4] = quad_bayer[SHIFT[i]['Y'] + 0::8, SHIFT[i]['X'] + 1::8]
        c[0::4, 2::4] = quad_bayer[SHIFT[i]['Y'] + 0::8, SHIFT[i]['X'] + 2::8]
        c[0::4, 3::4] = quad_bayer[SHIFT[i]['Y'] + 0::8, SHIFT[i]['X'] + 3::8]

        c[1::4, 0::4] = quad_bayer[SHIFT[i]['Y'] + 1::8, SHIFT[i]['X'] + 0::8]
        c[1::4, 1::4] = quad_bayer[SHIFT[i]['Y'] + 1::8, SHIFT[i]['X'] + 1::8]
        c[1::4, 2::4] = quad_bayer[SHIFT[i]['Y'] + 1::8, SHIFT[i]['X'] + 2::8]
        c[1::4, 3::4] = quad_bayer[SHIFT[i]['Y'] + 1::8, SHIFT[i]['X'] + 3::8]

        c[2::4, 0::4] = quad_bayer[SHIFT[i]['Y'] + 2::8, SHIFT[i]['X'] + 0::8]
        c[2::4, 1::4] = quad_bayer[SHIFT[i]['Y'] + 2::8, SHIFT[i]['X'] + 1::8]
        c[2::4, 2::4] = quad_bayer[SHIFT[i]['Y'] + 2::8, SHIFT[i]['X'] + 2::8]
        c[2::4, 3::4] = quad_bayer[SHIFT[i]['Y'] + 2::8, SHIFT[i]['X'] + 3::8]

        c[3::4, 0::4] = quad_bayer[SHIFT[i]['Y'] + 3::8, SHIFT[i]['X'] + 0::8]
        c[3::4, 1::4] = quad_bayer[SHIFT[i]['Y'] + 3::8, SHIFT[i]['X'] + 1::8]
        c[3::4, 2::4] = quad_bayer[SHIFT[i]['Y'] + 3::8, SHIFT[i]['X'] + 2::8]
        c[3::4, 3::4] = quad_bayer[SHIFT[i]['Y'] + 3::8, SHIFT[i]['X'] + 3::8]
    
    return chw

def QuadBayer2CHW(quad_bayer):
    assert len(quad_bayer.shape) == 2
    H, W = quad_bayer.shape[0], quad_bayer.shape[1]
    chw = np.zeros([4, H//2, W//2], dtype=quad_bayer.dtype)
    SHIFT = {    
        0: {'Y': 0, 'X': 0},    
        1: {'Y': 0, 'X': 2},    
        2: {'Y': 2, 'X': 0},    
        3: {'Y': 2, 'X': 2},   
    }
    for i, c in enumerate(chw):
        c[0::2, 0::2] = quad_bayer[SHIFT[i]['Y'] + 0::4, SHIFT[i]['X'] + 0::4]
        c[0::2, 1::2] = quad_bayer[SHIFT[i]['Y'] + 0::4, SHIFT[i]['X'] + 1::4]
        c[1::2, 0::2] = quad_bayer[SHIFT[i]['Y'] + 1::4, SHIFT[i]['X'] + 0::4]
        c[1::2, 1::2] = quad_bayer[SHIFT[i]['Y'] + 1::4, SHIFT[i]['X'] + 1::4]
    return chw

def CHW2RGB(CHW, bayer_pattern='BGGR'):
    if bayer_pattern == 'RGGB':
        r, g0, g1, b = CHW
        g = (g0 + g1)/2.0
        return np.stack([b, g, r], axis=-1)
    if bayer_pattern == 'GRBG':
        g0, r, b, g1 = CHW
        g = (g0 + g1)/2.0
        return np.stack([b, g, r], axis=-1)
    if bayer_pattern == 'BGGR':
        b, g0, g1, r = CHW
        g = (g0 + g1)/2.0
        return np.stack([b, g, r], axis=-1)
    # 默认返回RGGB
    r, g0, g1, b = CHW
    g = (g0 + g1)/2.0
    return np.stack([b, g, r], axis=-1)

# 主处理流程
if len(sys.argv) > 1:
    scenes = [sys.argv[1]]
else:
    scenes = sorted(os.listdir(UNPACK_RAW))

for scene in scenes:
    scene_path = os.path.join(UNPACK_RAW, scene)
    
    if not os.path.isdir(scene_path):
        print(scene_path)
        continue
    
    # 创建输出目录
    os.makedirs(os.path.join(os.path.join(ROOT, OUTPUT_DIR), scene), exist_ok=True)
    
    print(f"\n[处理] 场景: {scene}")
    
    # 1. 获取分辨率 - 优先从readme.txt，其次从raw文件名
    received_scene_name = remove_prefix(scene)
    readme_path = os.path.join(RECEIVED_ROOT, received_scene_name, 'readme.txt')
    
    W, H = parse_resolution_from_readme(readme_path)
    
    if W is None or H is None:
        # 尝试从第一个raw文件获取分辨率
        raw_files_temp = sorted(glob.glob(os.path.join(scene_path, '*.raw')))
        if raw_files_temp:
            W, H = parse_resolution_from_filename(raw_files_temp[0])
    
    if W is None or H is None:
        # 使用默认值
        W, H = DEFAULT_W, DEFAULT_H
        print(f"  [Warn] 使用默认分辨率: {W}x{H}")
    
    # 获取raw文件列表
    raw_files = sorted(glob.glob(os.path.join(scene_path, '*.raw')))
    
    for index, file in enumerate(raw_files):
        try:
            # 读取raw文件
            img = np.fromfile(file, dtype='uint16').reshape([H, W]).astype('float')
        
            # Quad Bayer转换
            img = QuadBayer2CHW(img)
            # img = HEX2CHW(img)  # hex模式
            # 转换为RGB
            img = CHW2RGB(img, BAYER_PATTERN)
            
            # 归一化
            img = (img - BP) / (WP - BP)
            img = img.clip(0, 1)
            
            # 读取YAML文件获取AWB增益
            yaml_path = os.path.join(YAML_DATA, scene, str(index).zfill(3) + '.yaml')
            if os.path.exists(yaml_path):
                with open(yaml_path, 'r', encoding='utf-8') as file_yaml:
                    yaml_content = yaml.safe_load(file_yaml)
                
                awb_b_gain = yaml_content.get('b_gain', 1.0)
                awb_r_gain = yaml_content.get('r_gain', 1.0)
                isp_gain = yaml_content.get('isp_gain', 1.0)
            else:
                print(f"  [Warn] YAML文件不存在: {yaml_path}, 使用默认增益")
                awb_b_gain = 1.0
                awb_r_gain = 1.0
                isp_gain = 1.0
            
            # 应用AWB增益
            img[..., 0] *= awb_b_gain  # B通道
            img[..., 2] *= awb_r_gain  # R通道
            img *= isp_gain
            
            # Gamma校正
            img = img ** (1 / GAMMA)
            
            # 转换为8位图像
            img = (img.clip(0, 1) * 255).astype('uint8')
            
            # 保存图像
            output_path = os.path.join(ROOT, OUTPUT_DIR, scene, 
                                      os.path.basename(file).replace('.raw', f'.{OUTPUT_TYPE}'))
            cv2.imwrite(output_path, img)
            
            if index == 0:
                print(f"b_gain: {awb_b_gain}, r_gain: {awb_r_gain}")
                print(f"  [Info] 处理第1帧: {os.path.basename(file)} -> {output_path}")
                
        except Exception as e:
            print(f"  [Error] 处理文件 {file} 时出错: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"  [Done] 场景 {scene}: {len(raw_files)} 帧处理完成")

print("\n" + "=" * 60)
print("全部场景处理完成")
print("=" * 60)