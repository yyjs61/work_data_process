import os, glob, natsort, shutil, numpy as np

# 配置路径
ROOT = r'D:\Data\2026_05\19\IMX06C_binning_normal_4k_20260514/'
RECEIVED = ROOT + 'received/'
MIPI_RAW = ROOT + 'unpack_raw/'

# 确保 unpack_raw 目录存在
os.makedirs(MIPI_RAW, exist_ok=True)

# 获取所有场景（忽略以.开头的文件和文件夹）
scenes = natsort.natsorted([s for s in os.listdir(RECEIVED) if not s.startswith('.')])

print(f"找到 {len(scenes)} 个场景需要处理")
print("=" * 70)

for id, scene in enumerate(scenes):
    scene_path = os.path.join(RECEIVED, scene)
    
    # 只处理文件夹，忽略文件
    if not os.path.isdir(scene_path):
        print(f"跳过文件: {scene}")
        continue
    
    # 创建输出目录
    output_dir = os.path.join(MIPI_RAW, str(id).zfill(2) + '_' + scene.replace(' ', '').replace(',', '_').replace('.', 'p'))
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n处理场景 [{id}]: {scene}")
    print(f"  输出目录: {output_dir}")
    
    # 获取场景下的所有 .raw 文件（忽略以.开头的文件）
    files = natsort.natsorted(glob.glob(os.path.join(scene_path, '*.raw')))
    # print(f"{scene} 有 {len(files)} 个raw文件")
    files = [f for f in files if not os.path.basename(f).startswith('._')]
    
    # 过滤：只处理大小为 16588800 的文件 (4096*3072*2 bytes = 16bit)
    files = natsort.natsorted([i for i in files if os.path.getsize(i) == 25165824])
    
    print(f"  找到 {len(files)} 个有效的 RAW 文件")
    
    for i, file in enumerate(files):
        output_filename = str(i).zfill(3) + '_' + os.path.basename(file)
        output_path = os.path.join(output_dir, output_filename)
        
        # 复制文件
        shutil.copy(file, output_path)
        
        # 进度显示
        if (i + 1) % 10 == 0 or (i + 1) == len(files):
            print(f"    已处理: {i + 1}/{len(files)}")

print("\n" + "=" * 70)
print("处理完成！")