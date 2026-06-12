import glob, natsort, os

ROOT = '/data/OVH9000_DCG_20260417_low_light/ace_pro2/'
UNPACK_RAW = ROOT + 'unpack_raw/'
RECEIVED = ROOT + 'received/'
YAMLS_DIR = ROOT + 'yamls_eachFrame/'
N_IMGS_PER_FILE = 50

EXAMPLE_META = '''
Black_level: 64.0
White_level: 16383.0
height: 3072.0
width: 4096.0
bayer_pattern: RGGB
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]

'''

def parseLine(line):
    values = line.split('[')[1:]
    values = [v.split(']')[0] for v in values]
    values = [float(v) if '.' in v else int(v) for v in values]
    return values

scene_folders = natsort.natsorted(glob.glob(os.path.join(UNPACK_RAW, '*')))

for folder in scene_folders:
    scene_name = os.path.basename(folder)
    
    # 去掉序号前缀，得到原始场景名
    if '__' in scene_name:
        raw_scene_name = scene_name.split('__', 1)[1]
    else:
        raw_scene_name = scene_name
    
    # 在 received 下找对应的场景文件夹
    received_folder = os.path.join(RECEIVED, raw_scene_name)
    
    if not os.path.exists(received_folder):
        print(f"跳过 {scene_name}: 找不到 {received_folder}")
        continue
    
    # 自动查找该文件夹下的第一个 .txt 文件
    txt_files = glob.glob(os.path.join(received_folder, '*.txt'))
    
    if not txt_files:
        print(f"跳过 {scene_name}: {received_folder} 下没有 txt 文件")
        continue
    
    received_txt = txt_files[0]
    print(f"处理: {scene_name} -> 使用 {os.path.basename(received_txt)}")
    
    with open(received_txt, 'r') as fi:
        lines = fi.readlines()
    
    # 创建对应的 yaml 输出目录
    yaml_output_dir = os.path.join(YAMLS_DIR, scene_name)
    os.makedirs(yaml_output_dir, exist_ok=True)
    
    for i in range(min(N_IMGS_PER_FILE, len(lines)//2)):
        line_AE = lines[2*i].strip()
        line_AWB = lines[2*i+1].strip()
        
        # AEINFO: F[0]S[19.982]I[160]AG[1.601]DG[1.000]
        f, s, iso, ag, dg = parseLine(line_AE)
        # AWBINFO: F[0]CT[6111]RG[8904]BG[6354]
        f, ct, rg, bg = parseLine(line_AWB)
        
        yaml_path = os.path.join(yaml_output_dir, f'{str(i).zfill(3)}.yaml')
        with open(yaml_path, 'w') as fo:
            fo.write(EXAMPLE_META)
            # gain = iso / 100
            gain = iso / 100.0
            fo.write(f'gain: {gain}\n')
            fo.write(f'iso: {iso}\n')
            fo.write(f'expotime: {int(s * 1000000)}\n')
            fo.write(f'isp_gain: {dg}\n')
            fo.write(f'SensorAGain: {ag}\n')
            fo.write(f'SensorDGain: {dg}\n')
            fo.write(f'cct: {ct}\n')
            fo.write(f'r_gain: {rg / 4096.0}\n')
            fo.write(f'b_gain: {bg / 4096.0}\n')
            fo.write(f'sensorgain: {gain}\n')
            fo.write(f'drc_gain: 1.0\n')
            fo.write(f'lux_index: 300\n')
            fo.write(f'luxid: 300\n')
    
    print(f"  完成 {min(N_IMGS_PER_FILE, len(lines)//2)} 个 yaml 文件 -> {yaml_output_dir}")