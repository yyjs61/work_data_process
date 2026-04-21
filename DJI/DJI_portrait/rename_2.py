import os
import glob
import natsort
import re

def add_prefix_to_scenes(root_path, prefix_length=2):
    """
    功能：给场景文件夹添加递增前缀（如 00__、01__）
    """
    if not os.path.exists(root_path):
        print(f"错误：目录不存在 -> {root_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"功能：给场景文件夹添加递增前缀")
    print(f"目标目录：{root_path}")
    print(f"{'='*60}")
    
    # 获取所有子文件夹（场景）
    scenes = [d for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d))]
    scenes = natsort.natsorted(scenes)
    
    print(f"找到场景数量：{len(scenes)}")
    
    for idx, scene in enumerate(scenes):
        old_path = os.path.join(root_path, scene)
        
        # 检查是否已有前缀
        if re.match(r'^\d{2}__', scene):
            print(f"  [跳过] {scene} (已有前缀)")
            continue
        
        # 生成新名称
        new_name = f"{str(idx).zfill(prefix_length)}__{scene}"
        new_path = os.path.join(root_path, new_name)
        
        # 检查目标是否已存在
        if os.path.exists(new_path):
            print(f"  [冲突] {scene} -> {new_name} (目标已存在)")
            continue
        
        try:
            os.rename(old_path, new_path)
            print(f"  [成功] {scene} -> {new_name}")
        except Exception as e:
            print(f"  [失败] {scene} 出错：{e}")
    
    print(f"场景前缀添加完成。")

def extract_frame_number(filename):
    """
    从文件名中提取帧编号
    例如：video_braw_dump__8597_4096x2304_72681477233.raw -> 8597
    """
    match = re.search(r'dump(?:_lofic)?__(\d+)_', filename)
    if match:
        return int(match.group(1))
    return None

def is_lofic_file(filename):
    """
    判断文件是否是 lofic 文件
    """
    return '_lofic_' in filename or 'dump_lofic' in filename

def add_prefix_to_files_by_frame_number(root_path, prefix_length=3):
    """
    功能：根据 raw 文件中的帧编号添加递增前缀
    【每个场景独立计数】
    lofic 文件在偶数位置（000, 002, 004...）
    非 lofic 文件在奇数位置（001, 003, 005...）
    """
    if not os.path.exists(root_path):
        print(f"错误：目录不存在 -> {root_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"功能：根据帧编号给 raw 文件添加递增前缀")
    print(f"规则：每个场景独立计数，lofic 在偶数位置，非 lofic 在奇数位置")
    print(f"目标目录：{root_path}")
    print(f"{'='*60}")
    
    # 获取所有场景文件夹
    scenes = [d for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d))]
    scenes = natsort.natsorted(scenes)
    
    for scene in scenes:
        scene_path = os.path.join(root_path, scene)
        raw_files = glob.glob(os.path.join(scene_path, '*.raw'))
        
        if not raw_files:
            print(f"  [跳过] {scene} (无 raw 文件)")
            continue
        
        print(f"\n  场景：{scene}")
        print(f"  找到 {len(raw_files)} 个 raw 文件")
        
        # 提取每个文件的帧编号和 lofic 标识
        file_info_map = []
        for file_path in raw_files:
            filename = os.path.basename(file_path)
            frame_num = extract_frame_number(filename)
            is_lofic = is_lofic_file(filename)
            if frame_num is not None:
                file_info_map.append({
                    'path': file_path,
                    'filename': filename,
                    'frame_num': frame_num,
                    'is_lofic': is_lofic
                })
            else:
                print(f"    [警告] 无法提取帧编号：{filename}")
        
        # 按帧编号排序，同一帧编号内 lofic 在前
        file_info_map.sort(key=lambda x: (x['frame_num'], 0 if x['is_lofic'] else 1))
        
        # 获取所有唯一的帧编号（保持顺序）
        unique_frames = []
        seen_frames = set()
        for info in file_info_map:
            if info['frame_num'] not in seen_frames:
                unique_frames.append(info['frame_num'])
                seen_frames.add(info['frame_num'])
        
        print(f"  发现 {len(unique_frames)} 个不同的帧编号")
        
        # 【关键修改】每个场景独立重置计数器
        scene_even_prefix = 0  # 偶数前缀（lofic）- 每个场景从 0 开始
        scene_odd_prefix = 1   # 奇数前缀（非 lofic）- 每个场景从 1 开始
        
        # 重命名文件
        count_renamed = 0
        for info in file_info_map:
            file_path = info['path']
            filename = info['filename']
            frame_num = info['frame_num']
            is_lofic = info['is_lofic']
            
            # 检查是否已有前缀
            if re.match(r'^\d{3}__', filename):
                print(f"    [跳过] {filename} (已有前缀)")
                continue
            
            # 根据是否是 lofic 文件分配前缀（每个场景独立计数）
            if is_lofic:
                prefix = str(scene_even_prefix).zfill(prefix_length)
                scene_even_prefix += 2  # 偶数递增：0, 2, 4...
                file_type = "lofic"
            else:
                prefix = str(scene_odd_prefix).zfill(prefix_length)
                scene_odd_prefix += 2   # 奇数递增：1, 3, 5...
                file_type = "normal"
            
            # 生成新名称
            new_name = f"{prefix}__{filename}"
            new_path = os.path.join(scene_path, new_name)
            
            # 检查目标是否已存在
            if os.path.exists(new_path):
                print(f"    [冲突] {filename} -> {new_name} (目标已存在)")
                continue
            
            try:
                os.rename(file_path, new_path)
                print(f"    [成功] {filename} -> {new_name} (帧:{frame_num}, {file_type})")
                count_renamed += 1
            except Exception as e:
                print(f"    [失败] {filename} 出错：{e}")
        
        print(f"  场景 {scene} 完成：{count_renamed} 个文件已重命名")
    
    print(f"\n文件前缀添加完成。")

def remove_prefix_from_scenes(root_path):
    """
    功能：移除场景文件夹的前缀（如 00__、01__）
    """
    if not os.path.exists(root_path):
        print(f"错误：目录不存在 -> {root_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"功能：移除场景文件夹的前缀")
    print(f"目标目录：{root_path}")
    print(f"{'='*60}")
    
    scenes = [d for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d))]
    scenes = natsort.natsorted(scenes)
    
    print(f"找到场景数量：{len(scenes)}")
    
    for scene in scenes:
        old_path = os.path.join(root_path, scene)
        
        match = re.match(r'^(\d{2}__)(.*)', scene)
        if not match:
            print(f"  [跳过] {scene} (无前缀)")
            continue
        
        new_name = match.group(2)
        new_path = os.path.join(root_path, new_name)
        
        if os.path.exists(new_path):
            print(f"  [冲突] {scene} -> {new_name} (目标已存在)")
            continue
        
        try:
            os.rename(old_path, new_path)
            print(f"  [成功] {scene} -> {new_name}")
        except Exception as e:
            print(f"  [失败] {scene} 出错：{e}")
    
    print(f"场景前缀移除完成。")

def remove_prefix_from_files(root_path):
    """
    功能：移除场景下文件的前缀（如 000__、001__）
    """
    if not os.path.exists(root_path):
        print(f"错误：目录不存在 -> {root_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"功能：移除场景下文件的前缀")
    print(f"目标目录：{root_path}")
    print(f"{'='*60}")
    
    scenes = [d for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d))]
    scenes = natsort.natsorted(scenes)
    
    for scene in scenes:
        scene_path = os.path.join(root_path, scene)
        raw_files = glob.glob(os.path.join(scene_path, '*.raw'))
        
        if not raw_files:
            print(f"  [跳过] {scene} (无 raw 文件)")
            continue
        
        print(f"\n  场景：{scene}")
        
        for file_path in raw_files:
            filename = os.path.basename(file_path)
            
            match = re.match(r'^(\d{3}__)(.*)', filename)
            if not match:
                print(f"    [跳过] {filename} (无前缀)")
                continue
            
            new_name = match.group(2)
            new_path = os.path.join(scene_path, new_name)
            
            if os.path.exists(new_path):
                print(f"    [冲突] {filename} -> {new_name} (目标已存在)")
                continue
            
            try:
                os.rename(file_path, new_path)
                print(f"    [成功] {filename} -> {new_name}")
            except Exception as e:
                print(f"    [失败] {filename} 出错：{e}")
    
    print(f"\n文件前缀移除完成。")

def main():
    # 配置路径
    ROOT = r"D:\Data\DJI_OV50X\20260420\20260417_portrait\unpack_raw"
    
    print("="*60)
    print("文件重命名工具 - 基于帧编号（每场景独立计数）")
    print("="*60)
    print(f"ROOT: {ROOT}")
    print("="*60)
    
    # 步骤 1：给场景添加前缀
    add_prefix_to_scenes(ROOT)
    
    # 步骤 2：给 raw 文件基于帧编号添加前缀（每场景独立计数）
    # add_prefix_to_files_by_frame_number(ROOT)
    
    print("\n" + "="*60)
    print("所有操作完成！")
    print("="*60)

if __name__ == "__main__":
    main()