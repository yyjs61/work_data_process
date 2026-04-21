import os
import glob
import natsort
import re

def replace_dot_in_scene_name(scene_name):
    """
    将场景名中的 '.' 替换为 'p'
    """
    return scene_name.replace('.', 'p')

def add_prefix_to_scenes(root_path, prefix_length=2):
    """
    功能 1：将场景名中的 '.' 替换为 'p'，并添加递增前缀
    """
    if not os.path.exists(root_path):
        print(f"错误：目录不存在 -> {root_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"功能 1：处理场景文件夹（替换 '.' 为 'p' + 添加前缀）")
    print(f"目标目录：{root_path}")
    print(f"{'='*60}")
    
    # 获取所有子文件夹（场景）
    scenes = [d for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d))]
    scenes = natsort.natsorted(scenes)
    
    print(f"找到场景数量：{len(scenes)}")
    
    for idx, scene in enumerate(scenes):
        old_path = os.path.join(root_path, scene)
        
        # 第一步：将 '.' 替换为 'p'
        new_scene_name = replace_dot_in_scene_name(scene)
        
        # 第二步：添加递增前缀
        new_scene_name = f"{str(idx).zfill(prefix_length)}__{new_scene_name}"
        
        new_path = os.path.join(root_path, new_scene_name)
        
        # 如果名称没有变化，跳过
        if scene == new_scene_name:
            print(f"  [跳过] {scene} (无需修改)")
            continue
        
        # 检查目标是否已存在
        if os.path.exists(new_path):
            print(f"  [冲突] {scene} -> {new_scene_name} (目标已存在)")
            continue
        
        try:
            os.rename(old_path, new_path)
            print(f"  [成功] {scene} -> {new_scene_name}")
        except Exception as e:
            print(f"  [失败] {scene} 出错：{e}")
    
    print(f"场景文件夹处理完成。")

def add_prefix_to_files(root_path, prefix_length=3):
    """
    功能 2：给 raw 文件添加前缀
    _2.raw → 偶数前缀 (000__, 002__, 004__...)
    _0.raw → 奇数前缀 (001__, 003__, 005__...)
    """
    if not os.path.exists(root_path):
        print(f"错误：目录不存在 -> {root_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"功能 2：给 raw 文件添加前缀")
    print(f"规则：_2.raw → 偶数前缀，_0.raw → 奇数前缀")
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
        
        # 分离 _2.raw 和 _0.raw 文件
        files_2 = []  # _2.raw 文件（偶数前缀）
        files_0 = []  # _0.raw 文件（奇数前缀）
        
        for file_path in raw_files:
            filename = os.path.basename(file_path)
            if '_2.raw' in filename:
                files_2.append(file_path)
            elif '_0.raw' in filename:
                files_0.append(file_path)
            else:
                print(f"    [警告] 未知文件类型：{filename}")
        
        # 自然排序
        files_2 = natsort.natsorted(files_2)
        files_0 = natsort.natsorted(files_0)
        
        print(f"    _2.raw 文件数：{len(files_2)}")
        print(f"    _0.raw 文件数：{len(files_0)}")
        
        # 合并文件列表，按帧编号排序
        # 假设文件名为：0000_2.raw, 0000_0.raw, 0001_2.raw, 0001_0.raw...
        # 我们需要按帧编号（0000, 0001...）排序
        all_files = []
        for file_path in files_2 + files_0:
            filename = os.path.basename(file_path)
            # 提取帧编号（文件名中 _2.raw 或 _0.raw 之前的部分）
            match = re.match(r'(\d+)_', filename)
            if match:
                frame_num = int(match.group(1))
                is_even_type = '_2.raw' in filename  # True 表示 _2.raw，False 表示 _0.raw
                all_files.append({
                    'path': file_path,
                    'filename': filename,
                    'frame_num': frame_num,
                    'is_even_type': is_even_type
                })
        
        # 按帧编号排序
        all_files.sort(key=lambda x: (x['frame_num'], 0 if x['is_even_type'] else 1))
        
        # 分配前缀
        even_counter = 0  # 偶数前缀计数器 (000, 002, 004...)
        odd_counter = 1   # 奇数前缀计数器 (001, 003, 005...)
        
        count_renamed = 0
        for file_info in all_files:
            file_path = file_info['path']
            filename = file_info['filename']
            
            # 检查是否已有前缀
            if re.match(r'^\d{3}__', filename):
                print(f"    [跳过] {filename} (已有前缀)")
                continue
            
            # 根据文件类型分配前缀
            if file_info['is_even_type']:
                # _2.raw → 偶数前缀
                prefix = str(even_counter).zfill(prefix_length)
                even_counter += 2
                file_type = "_2.raw (偶数)"
            else:
                # _0.raw → 奇数前缀
                prefix = str(odd_counter).zfill(prefix_length)
                odd_counter += 2
                file_type = "_0.raw (奇数)"
            
            # 生成新名称
            new_name = f"{prefix}__{filename}"
            new_path = os.path.join(scene_path, new_name)
            
            # 检查目标是否已存在
            if os.path.exists(new_path):
                print(f"    [冲突] {filename} -> {new_name} (目标已存在)")
                continue
            
            try:
                os.rename(file_path, new_path)
                print(f"    [成功] {filename} -> {new_name} ({file_type})")
                count_renamed += 1
            except Exception as e:
                print(f"    [失败] {filename} 出错：{e}")
        
        print(f"  场景 {scene} 完成：{count_renamed} 个文件已重命名")
    
    print(f"\n文件前缀添加完成。")

def remove_prefix_from_scenes(root_path):
    """
    功能 3：移除场景文件夹的前缀
    """
    if not os.path.exists(root_path):
        print(f"错误：目录不存在 -> {root_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"功能 3：移除场景文件夹的前缀")
    print(f"目标目录：{root_path}")
    print(f"{'='*60}")
    
    scenes = [d for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d))]
    scenes = natsort.natsorted(scenes)
    
    print(f"找到场景数量：{len(scenes)}")
    
    for scene in scenes:
        old_path = os.path.join(root_path, scene)
        
        # 检查是否有前缀
        match = re.match(r'^(\d{2}__)(.*)', scene)
        if not match:
            print(f"  [跳过] {scene} (无前缀)")
            continue
        
        # 生成新名称（移除前缀）
        new_name = match.group(2)
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
    
    print(f"场景前缀移除完成。")

def remove_prefix_from_files(root_path):
    """
    功能 4：移除场景下文件的前缀
    """
    if not os.path.exists(root_path):
        print(f"错误：目录不存在 -> {root_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"功能 4：移除场景下文件的前缀")
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
            
            # 检查是否有前缀
            match = re.match(r'^(\d{3}__)(.*)', filename)
            if not match:
                print(f"    [跳过] {filename} (无前缀)")
                continue
            
            # 生成新名称（移除前缀）
            new_name = match.group(2)
            new_path = os.path.join(scene_path, new_name)
            
            # 检查目标是否已存在
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
    ROOT = r"D:\Data\DJI_OV50X\20260420\20260417_dcg_lofic\unpack_raw"
    
    print("="*60)
    print("文件重命名工具")
    print("="*60)
    print(f"ROOT: {ROOT}")
    print("="*60)
    
    # 步骤 1：处理场景文件夹（替换 '.' 为 'p' + 添加前缀）
    add_prefix_to_scenes(ROOT)
    
    # 步骤 2：给 raw 文件添加前缀
    add_prefix_to_files(ROOT)
    
    print("\n" + "="*60)
    print("所有操作完成！")
    print("="*60)

if __name__ == "__main__":
    main()