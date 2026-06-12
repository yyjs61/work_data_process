import os
import shutil

def split_raw_files():
    """
    将black_level目录下的RAW文件分割成单独的帧
    """
    base_dir = r"D:\Data\2026_06\11\HY_IMX06A_20260601"
    source_dir = os.path.join(base_dir, "testdata")
    target_dir = os.path.join(base_dir, "unpack_raw")
    
    # RAW文件参数
    width = 3840
    height = 2160
    bits_per_pixel = 16  # 每个像素占16bit（2字节）
    frame_size = width * height * (bits_per_pixel // 8)  # 每帧字节数: 3840*2160*2 = 16,588,800 bytes
    
    print(f"每帧大小: {frame_size:,} 字节 ({frame_size/1024/1024:.2f} MB)")
    print(f"源目录: {source_dir}")
    print(f"目标目录: {target_dir}")
    print("="*80)
    
    # 创建目标根目录
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"创建目录: {target_dir}")
    
    # 统计信息
    total_scenes = 0
    total_files = 0
    total_frames = 0
    
    # 遍历black_level下的所有场景文件夹
    for scene_name in sorted(os.listdir(source_dir)):
        scene_source_path = os.path.join(source_dir, scene_name)
        
        # 只处理文件夹
        if not os.path.isdir(scene_source_path):
            continue
        
        total_scenes += 1
        print(f"\n处理场景 [{total_scenes}]: {scene_name}")
        print("-" * 60)
        
        # 创建目标场景目录
        scene_target_path = os.path.join(target_dir, scene_name)
        if not os.path.exists(scene_target_path):
            os.makedirs(scene_target_path)
            print(f"  创建目录: {scene_name}")
        
        # 遍历场景下的所有RAW文件
        raw_files = [f for f in os.listdir(scene_source_path) if f.endswith('.raw')]
        
        for raw_file in raw_files:
            source_file_path = os.path.join(scene_source_path, raw_file)
            file_size = os.path.getsize(source_file_path)
            
            # 计算帧数
            num_frames = file_size // frame_size
            
            print(f"\n  文件: {raw_file}")
            print(f"  文件大小: {file_size:,} 字节 ({file_size/1024/1024:.2f} MB)")
            print(f"  帧数: {num_frames}")
            
            # 获取文件名（不含扩展名）
            base_name = os.path.splitext(raw_file)[0]
            
            # 读取并分割RAW文件
            with open(source_file_path, 'rb') as f:
                for frame_idx in range(num_frames):
                    # 读取一帧数据
                    frame_data = f.read(frame_size)
                    
                    if len(frame_data) != frame_size:
                        print(f"    警告: 第{frame_idx}帧数据不完整!")
                        break
                    
                    # 生成目标文件名（添加两位数字后缀）
                    target_filename = f"{base_name}_{frame_idx:02d}.raw"
                    target_file_path = os.path.join(scene_target_path, target_filename)
                    
                    # 写入目标文件
                    with open(target_file_path, 'wb') as out_f:
                        out_f.write(frame_data)
                    
                    total_frames += 1
            
            total_files += 1
            print(f"  ✓ 完成分割: {num_frames} 帧")
    
    # 打印统计信息
    print("\n" + "="*80)
    print("处理完成!")
    print(f"  场景数: {total_scenes}")
    print(f"  RAW文件数: {total_files}")
    print(f"  总帧数: {total_frames}")
    print(f"  输出目录: {target_dir}")
    print("="*80)


def verify_split_results():
    """
    验证分割结果
    """
    base_dir = r"D:\Data\2026_06\11\HY_IMX06A_20260601"
    target_dir = os.path.join(base_dir, "unpack_raw")
    
    print("\n验证分割结果:")
    print("="*80)
    
    if not os.path.exists(target_dir):
        print("目标目录不存在!")
        return
    
    total_files = 0
    total_size = 0
    
    for scene_name in sorted(os.listdir(target_dir)):
        scene_path = os.path.join(target_dir, scene_name)
        if not os.path.isdir(scene_path):
            continue
        
        raw_files = [f for f in os.listdir(scene_path) if f.endswith('.raw')]
        scene_size = sum(os.path.getsize(os.path.join(scene_path, f)) for f in raw_files)
        
        print(f"\n{scene_name}:")
        print(f"  文件数: {len(raw_files)}")
        print(f"  总大小: {scene_size/1024/1024:.2f} MB")
        
        # 显示前5个和最后5个文件
        if raw_files:
            raw_files.sort()
            print(f"  示例文件:")
            for f in raw_files[:3]:
                size = os.path.getsize(os.path.join(scene_path, f))
                print(f"    - {f} ({size/1024/1024:.2f} MB)")
            if len(raw_files) > 5:
                print(f"    ...")
            for f in raw_files[-2:]:
                size = os.path.getsize(os.path.join(scene_path, f))
                print(f"    - {f} ({size/1024/1024:.2f} MB)")
        
        total_files += len(raw_files)
        total_size += scene_size
    
    print("\n" + "="*80)
    print(f"总计: {total_files} 个文件, {total_size/1024/1024:.2f} MB")
    print("="*80)


if __name__ == "__main__":
    # 执行分割
    split_raw_files()
    
    # 验证结果
    verify_split_results()