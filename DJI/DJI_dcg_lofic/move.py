import os
import glob
import shutil
import natsort
import rawpy
import numpy as np

# 源目录：received文件夹
SRC = r'D:\Data\DJI_OV50X\20260420\20260417_dcg_lofic\received'
DST = r'D:\Data\DJI_OV50X\20260420\20260417_dcg_lofic/unpack_raw'

# 获取所有场景（子文件夹）
scenes = natsort.natsorted(os.listdir(SRC))

# 可选：指定特定场景或过滤场景
# scenes = ['01x', '02x', '04x', '08x', '16x', '32x', '64x', '128x', '255x']

for j, scene in enumerate(scenes):
    scene_path = os.path.join(SRC, scene)
    
    # 跳过文件，只处理文件夹
    if not os.path.isdir(scene_path):
        continue
    
    # 创建目标场景文件夹
    dst_scene = os.path.join(DST, scene)
    os.makedirs(dst_scene, exist_ok=True)
    
    # 获取场景下所有.dng文件
    files = natsort.natsorted(glob.glob(os.path.join(scene_path, '*.dng')))
    
    # 可选：根据文件大小过滤（示例中的大小是100664938，根据实际情况调整或注释掉）
    # files = natsort.natsorted([f for f in files if os.path.getsize(f) == 100664938])
    
    # 可选：只处理一部分文件（例如第30到130个）
    # files = files[30:130]
    
    print(f"处理场景 [{j+1}/{len(scenes)}]: {scene}, 共 {len(files)} 个DNG文件")
    
    for idx, file in enumerate(files):
        try:
            # 使用rawpy 读
            with rawpy.imread(file) as raw:
                # 提取原始raw图像数据（未去马赛克）
                img = raw.raw_image
                
                # 保存为.raw文件（二进制格式）
                output_filename = os.path.basename(file).replace('.dng', '.raw')
                output_path = os.path.join(dst_scene, output_filename)
                img.tofile(output_path)
                
                if (idx + 1) % 50 == 0:
                    print(f"  已处理 {idx+1}/{len(files)} 个文件")
                    
        except Exception as e:
            print(f"  处理失败: {os.path.basename(file)}, 错误: {e}")

print("所有场景处理完成！")