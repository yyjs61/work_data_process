import os
import glob
import natsort

def add_suffix_to_raw_files(root_path):
    """
    为 unpack_raw 目录下每个场景的 raw 文件添加后缀：
    含 "lofic" 或 偶数前缀 → __short.raw
    不含 "lofic" 或 奇数前缀 → __long.raw
    """
    if not os.path.exists(root_path):
        print(f"错误：目录不存在 -> {root_path}")
        return
    
    if not os.path.isdir(root_path):
        print(f"错误：路径不是目录 -> {root_path}")
        return
    
    print(f"目标目录：{root_path}")
    print("操作：为 raw 文件添加后缀 (lofic→__short, 其他→__long)")
    print("=" * 60)
    
    # 获取所有场景文件夹
    scenes = [d for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d))]
    scenes = natsort.natsorted(scenes)
    
    print(f"找到场景数量：{len(scenes)}")
    
    count_short = 0
    count_long = 0
    count_skip = 0
    count_errors = 0
    
    for scene in scenes:
        scene_path = os.path.join(root_path, scene)
        raw_files = glob.glob(os.path.join(scene_path, '*.raw'))
        
        if not raw_files:
            print(f"  [跳过] {scene} (无 raw 文件)")
            continue
        
        print(f"\n处理场景：{scene}")
        print(f"  找到 {len(raw_files)} 个 raw 文件")
        
        # 自然排序
        raw_files = natsort.natsorted(raw_files)
        
        for file_path in raw_files:
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            
            # 方法1：根据文件名是否包含 "lofic" 判断
            if 'lofic' in filename.lower():
                new_filename = f"{name}__short{ext}"
                file_type = "lofic → __short"
                count_short += 1
            else:
                new_filename = f"{name}__long{ext}"
                file_type = "normal → __long"
                count_long += 1
            
            # 方法2（备选）：根据前缀奇偶判断
            # prefix_match = re.match(r'^(\d+)_', filename)
            # if prefix_match:
            #     prefix_num = int(prefix_match.group(1))
            #     if prefix_num % 2 == 0:  # 偶数
            #         new_filename = f"{name}__short{ext}"
            #         file_type = f"even({prefix_num}) → __short"
            #     else:  # 奇数
            #         new_filename = f"{name}__long{ext}"
            #         file_type = f"odd({prefix_num}) → __long"
            
            new_path = os.path.join(scene_path, new_filename)
            
            # 检查目标文件是否已存在
            if os.path.exists(new_path):
                print(f"    [冲突] {filename} -> {new_filename} (目标已存在)")
                count_skip += 1
                continue
            
            try:
                # 执行重命名
                os.rename(file_path, new_path)
                print(f"    [成功] {filename} -> {new_filename} ({file_type})")
            except Exception as e:
                print(f"    [失败] {filename} 出错：{e}")
                count_errors += 1
    
    print("\n" + "=" * 60)
    print("处理完成！")
    print(f"添加 __short 后缀：{count_short} 个文件")
    print(f"添加 __long 后缀：{count_long} 个文件")
    print(f"跳过：{count_skip} 个文件")
    print(f"失败：{count_errors} 个文件")
    print("=" * 60)

if __name__ == "__main__":
    # 配置路径
    ROOT = r"D:\Data\DJI_OV50X\20260420\20260417_portrait\unpack_raw"
    
    print("=" * 60)
    print("RAW 文件后缀添加工具")
    print("=" * 60)
    print(f"ROOT: {ROOT}")
    print("=" * 60)
    
    # 执行处理
    add_suffix_to_raw_files(ROOT)
    
    # 防止窗口闪退
    input("\n按回车键退出...")