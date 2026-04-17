import os
import re
import glob
import natsort

# ==================== 配置区域 ====================
ROOT = r"D:\Data\20260417\honor\received"
CPATH = r"\inner_ISO902_10ms"
FILE_PATTERN = "*.mp4"  # 可修改为 "*.mp4" 或其他
# ==================== 配置区域结束 ====================

def natural_sort(items):
    """
    自然排序（按数字大小排序，而不是字典序）
    """
    return natsort.natsorted(items)

def add_prefix_to_scenes(root_path, prefix_length=2):
    """
    功能 1：给场景文件夹添加递增前缀（如 00__、01__）
    """
    target_dir = os.path.join(root_path, CPATH.lstrip('\\'))
    
    if not os.path.exists(target_dir):
        print(f"错误：目录不存在 -> {target_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"功能 1：给场景文件夹添加递增前缀")
    print(f"目标目录：{target_dir}")
    print(f"{'='*60}")
    
    # 获取所有子文件夹（场景）
    scenes = [d for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))]
    scenes = natural_sort(scenes)
    
    print(f"找到场景数量：{len(scenes)}")
    
    for idx, scene in enumerate(scenes):
        old_path = os.path.join(target_dir, scene)
        
        # 检查是否已有前缀
        if re.match(r'^\d{2}__', scene):
            print(f"  [跳过] {scene} (已有前缀)")
            continue
        
        # 生成新名称
        new_name = f"{str(idx).zfill(prefix_length)}__{scene}"
        new_path = os.path.join(target_dir, new_name)
        
        # 检查目标是否已存在
        if os.path.exists(new_path):
            print(f"  [冲突] {scene} -> {new_name} (目标已存在)")
            continue
        
        try:
            os.rename(old_path, new_path)
            print(f"  [成功] {scene} -> {new_name}")
        except Exception as e:
            print(f"  [失败] {scene} 出错：{e}")
    
    print(f"功能 1 完成。")

def add_prefix_to_files(root_path, prefix_length=2):
    """
    功能 2：给场景下的特定文件添加递增前缀（如 000__、001__）
    """
    target_dir = os.path.join(root_path, CPATH.lstrip('\\'))
    
    if not os.path.exists(target_dir):
        print(f"错误：目录不存在 -> {target_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"功能 2：给场景下的文件添加递增前缀")
    print(f"文件模式：{FILE_PATTERN}")
    print(f"{'='*60}")
    
    # 获取所有场景文件夹
    scenes = [d for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))]
    scenes = natural_sort(scenes)
    
    for scene in scenes:
        scene_path = os.path.join(target_dir, scene)
        files = glob.glob(os.path.join(scene_path, FILE_PATTERN))
        files = natural_sort(files)
        
        if not files:
            print(f"  [跳过] {scene} (无匹配文件)")
            continue
        
        print(f"\n  场景：{scene}")
        
        for idx, file_path in enumerate(files):
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            
            # 检查是否已有前缀
            if re.match(r'^\d{3}__', name):
                print(f"    [跳过] {filename} (已有前缀)")
                continue
            
            # 生成新名称
            new_name = f"{str(idx).zfill(prefix_length)}__{filename}"
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
    
    print(f"功能 2 完成。")

def remove_prefix_from_scenes(root_path):
    """
    功能 3：移除场景文件夹的前缀（如 00__、01__）
    """
    target_dir = os.path.join(root_path, CPATH.lstrip('\\'))
    
    if not os.path.exists(target_dir):
        print(f"错误：目录不存在 -> {target_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"功能 3：移除场景文件夹的前缀")
    print(f"目标目录：{target_dir}")
    print(f"{'='*60}")
    
    # 获取所有子文件夹（场景）
    scenes = [d for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))]
    scenes = natural_sort(scenes)
    
    print(f"找到场景数量：{len(scenes)}")
    
    for scene in scenes:
        old_path = os.path.join(target_dir, scene)
        
        # 检查是否有前缀
        match = re.match(r'^(\d{2}__)(.*)', scene)
        if not match:
            print(f"  [跳过] {scene} (无前缀)")
            continue
        
        # 生成新名称（移除前缀）
        new_name = match.group(2)
        new_path = os.path.join(target_dir, new_name)
        
        # 检查目标是否已存在
        if os.path.exists(new_path):
            print(f"  [冲突] {scene} -> {new_name} (目标已存在)")
            continue
        
        try:
            os.rename(old_path, new_path)
            print(f"  [成功] {scene} -> {new_name}")
        except Exception as e:
            print(f"  [失败] {scene} 出错：{e}")
    
    print(f"功能 3 完成。")

def remove_prefix_from_files(root_path):
    """
    功能 4：移除场景下文件的前缀（如 000__、001__）
    """
    target_dir = os.path.join(root_path, CPATH.lstrip('\\'))
    
    if not os.path.exists(target_dir):
        print(f"错误：目录不存在 -> {target_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"功能 4：移除场景下文件的前缀")
    print(f"文件模式：{FILE_PATTERN}")
    print(f"{'='*60}")
    
    # 获取所有场景文件夹
    scenes = [d for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))]
    scenes = natural_sort(scenes)
    
    for scene in scenes:
        scene_path = os.path.join(target_dir, scene)
        files = glob.glob(os.path.join(scene_path, FILE_PATTERN))
        files = natural_sort(files)
        
        if not files:
            print(f"  [跳过] {scene} (无匹配文件)")
            continue
        
        print(f"\n  场景：{scene}")
        
        for file_path in files:
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            
            # 检查是否有前缀
            match = re.match(r'^(\d{3}__)(.*)', name)
            if not match:
                print(f"    [跳过] {filename} (无前缀)")
                continue
            
            # 生成新名称（移除前缀）
            new_name = match.group(2) + ext
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
    
    print(f"功能 4 完成。")

def rename_files_to_sequence(root_path, prefix_length=3):
    """
    功能 5：将场景下的特定文件重命名为递增序号（如 000.raw、001.raw）
    """
    target_dir = os.path.join(root_path, CPATH.lstrip('\\'))
    
    if not os.path.exists(target_dir):
        print(f"错误：目录不存在 -> {target_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"功能 5：将文件重命名为递增序号")
    print(f"文件模式：{FILE_PATTERN}")
    print(f"{'='*60}")
    
    # 获取所有场景文件夹
    scenes = [d for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))]
    scenes = natural_sort(scenes)
    
    for scene in scenes:
        scene_path = os.path.join(target_dir, scene)
        files = glob.glob(os.path.join(scene_path, FILE_PATTERN))
        files = natural_sort(files)
        
        if not files:
            print(f"  [跳过] {scene} (无匹配文件)")
            continue
        
        print(f"\n  场景：{scene}")
        
        # 获取文件扩展名（假设同一场景下扩展名一致）
        _, ext = os.path.splitext(files[0])
        
        for idx, file_path in enumerate(files):
            filename = os.path.basename(file_path)
            
            # 生成新名称（纯序号 + 扩展名）
            new_name = f"{str(idx).zfill(prefix_length)}{ext}"
            new_path = os.path.join(scene_path, new_name)
            
            # 如果文件名已符合目标，跳过
            if filename == new_name:
                print(f"    [跳过] {filename} (已符合目标)")
                continue
            
            # 检查目标是否已存在
            if os.path.exists(new_path):
                print(f"    [冲突] {filename} -> {new_name} (目标已存在)")
                continue
            
            try:
                os.rename(file_path, new_path)
                print(f"    [成功] {filename} -> {new_name}")
            except Exception as e:
                print(f"    [失败] {filename} 出错：{e}")
    
    print(f"功能 5 完成。")

def replace_dot_in_scenes(root_path):
    """
    功能 6：将场景名中的'.'替换为'p'
    """
    target_dir = os.path.join(root_path, CPATH.lstrip('\\'))
    
    if not os.path.exists(target_dir):
        print(f"错误：目录不存在 -> {target_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"功能 6：将场景名中的'.'替换为'p'")
    print(f"目标目录：{target_dir}")
    print(f"{'='*60}")
    
    # 获取所有子文件夹（场景）
    scenes = [d for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))]
    scenes = natural_sort(scenes)
    
    print(f"找到场景数量：{len(scenes)}")
    
    count_replaced = 0
    
    for scene in scenes:
        old_path = os.path.join(target_dir, scene)
        
        # 检查是否包含'.'
        if '.' not in scene:
            print(f"  [跳过] {scene} (不含'.')")
            continue
        
        # 替换'.'为'p'
        new_name = scene.replace('.', 'p')
        new_path = os.path.join(target_dir, new_name)
        
        # 检查目标是否已存在
        if os.path.exists(new_path):
            print(f"  [冲突] {scene} -> {new_name} (目标已存在)")
            continue
        
        try:
            os.rename(old_path, new_path)
            print(f"  [成功] {scene} -> {new_name}")
            count_replaced += 1
        except Exception as e:
            print(f"  [失败] {scene} 出错：{e}")
    
    print(f"功能 6 完成。共替换 {count_replaced} 个场景名。")

def replace_dot_in_files(root_path):
    """
    功能 7：将文件名中的'.'（除了后缀的）替换为'p'
    """
    target_dir = os.path.join(root_path, CPATH.lstrip('\\'))
    
    if not os.path.exists(target_dir):
        print(f"错误：目录不存在 -> {target_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"功能 7：将文件名中的'.'（除了后缀的）替换为'p'")
    print(f"文件模式：{FILE_PATTERN}")
    print(f"{'='*60}")
    
    # 获取所有场景文件夹
    scenes = [d for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))]
    scenes = natural_sort(scenes)
    
    count_replaced = 0
    
    for scene in scenes:
        scene_path = os.path.join(target_dir, scene)
        files = glob.glob(os.path.join(scene_path, FILE_PATTERN))
        files = natural_sort(files)
        
        if not files:
            print(f"  [跳过] {scene} (无匹配文件)")
            continue
        
        print(f"\n  场景：{scene}")
        
        for file_path in files:
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            
            # 检查文件名（不含后缀）是否包含'.'
            if '.' not in name:
                print(f"    [跳过] {filename} (文件名不含'.')")
                continue
            
            # 替换文件名中的'.'为'p'（保留后缀）
            new_name = name.replace('.', 'p') + ext
            new_path = os.path.join(scene_path, new_name)
            
            # 检查目标是否已存在
            if os.path.exists(new_path):
                print(f"    [冲突] {filename} -> {new_name} (目标已存在)")
                continue
            
            try:
                os.rename(file_path, new_path)
                print(f"    [成功] {filename} -> {new_name}")
                count_replaced += 1
            except Exception as e:
                print(f"    [失败] {filename} 出错：{e}")
    
    print(f"功能 7 完成。共替换 {count_replaced} 个文件名。")

def main(functions=None):
    """
    主函数 - 接口形式
    :param functions: 要执行的功能列表，如 [1, 2, 6, 7]
                      如果为 None，则执行所有功能
    """
    print("="*60)
    print("文件重命名工具")
    print("="*60)
    print(f"ROOT: {ROOT}")
    print(f"CPATH: {CPATH}")
    print(f"FILE_PATTERN: {FILE_PATTERN}")
    print("="*60)
    
    # 功能映射
    function_map = {
        1: ("给场景文件夹添加递增前缀", lambda: add_prefix_to_scenes(ROOT)),
        2: ("给场景下的文件添加递增前缀", lambda: add_prefix_to_files(ROOT)),
        3: ("移除场景文件夹的前缀", lambda: remove_prefix_from_scenes(ROOT)),
        4: ("移除场景下文件的前缀", lambda: remove_prefix_from_files(ROOT)),
        5: ("将文件重命名为递增序号", lambda: rename_files_to_sequence(ROOT)),
        6: ("将场景名中的'.'替换为'p'", lambda: replace_dot_in_scenes(ROOT)),
        7: ("将文件名中的'.'替换为'p'", lambda: replace_dot_in_files(ROOT)),
    }
    
    # 如果未指定功能，默认执行所有功能
    if functions is None:
        functions = list(function_map.keys())
    
    # 验证功能编号
    invalid_functions = [f for f in functions if f not in function_map]
    if invalid_functions:
        print(f"警告：无效的功能编号 {invalid_functions}，将被忽略")
        functions = [f for f in functions if f in function_map]
    
    if not functions:
        print("没有要执行的功能。")
        return
    
    print(f"\n将执行以下功能：{functions}")
    print("="*60)
    
    # 执行选择的功能
    for func_id in functions:
        func_name, func = function_map[func_id]
        print(f"\n>>> 开始执行功能 {func_id}: {func_name}")
        try:
            func()
        except Exception as e:
            print(f"功能 {func_id} 执行失败：{e}")
    
    print("\n" + "="*60)
    print("所有功能执行完毕。")
    print("="*60)

# ==================== 使用示例 ====================
if __name__ == "__main__":
    # 示例 1：执行所有功能
    # main()
    
    # 示例 2：只执行功能 1 和 2
    # main([1, 2])
    
    # 示例 3：只执行新功能 6 和 7
    # main([6, 7])
    
    # 示例 4：执行多个功能
    main([1])