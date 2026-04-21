import os
import glob
import natsort

def add_suffix_to_raw_files(root_path):
    """
    为 unpack_raw 目录下每个场景的 raw 文件添加后缀：
    _2.raw → _2_lofic.raw
    _0.raw → _0_dcg.raw
    """
    if not os.path.exists(root_path):
        print(f"错误：目录不存在 -> {root_path}")
        return
    
    if not os.path.isdir(root_path):
        print(f"错误：路径不是目录 -> {root_path}")
        return
    
    print(f"目标目录：{root_path}")
    print("操作：为 raw 文件添加后缀 (_2→_lofic, _0→_dcg)")
    print("=" * 60)
    
    # 获取所有场景文件夹
    scenes = [d for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d))]
    scenes = natsort.natsorted(scenes)
    
    print(f"找到场景数量：{len(scenes)}")
    
    count_renamed = 0
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
            
            # 判断文件类型并生成新文件名
            # if '_2.raw' in filename:
            #     # _2.raw → _2_lofic.raw
            #     new_filename = filename.replace('_2.raw', '_2_lofic.raw')
            #     file_type = "_2 → _2_lofic"
            # elif '_0.raw' in filename:
            #     # _0.raw → _0_dcg.raw
            #     new_filename = filename.replace('_0.raw', '_0_dcg.raw')
            #     file_type = "_0 → _0_dcg"
            if '_2_lofic.raw' in filename:
                # _2.raw → _2_lofic.raw
                new_filename = filename.replace('_2_lofic.raw', '_2_lofic__short.raw')
                file_type = "_2 → _2_lofic-> short"
            elif '_0_dcg.raw' in filename:
                # _0.raw → _0_dcg.raw
                new_filename = filename.replace('_0_dcg.raw', '_0_dcg__long.raw')
                file_type = "_0 → _0_dcg -> long"
            else:
                # 不匹配的文件，跳过
                print(f"    [跳过] {filename} (不匹配的模式)")
                count_skip += 1
                continue
            
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
                count_renamed += 1
            except Exception as e:
                print(f"    [失败] {filename} 出错：{e}")
                count_errors += 1
    
    print("\n" + "=" * 60)
    print("处理完成！")
    print(f"成功重命名：{count_renamed} 个文件")
    print(f"跳过：{count_skip} 个文件")
    print(f"失败：{count_errors} 个文件")
    print("=" * 60)

if __name__ == "__main__":
    # 配置路径
    ROOT = r"D:\Data\DJI_OV50X\20260420\20260417_dcg_lofic\unpack_raw"
    
    print("=" * 60)
    print("RAW 文件后缀添加工具")
    print("=" * 60)
    print(f"ROOT: {ROOT}")
    print("=" * 60)
    
    # 执行处理
    
    add_suffix_to_raw_files(ROOT)
    
    # 防止窗口闪退
    input("\n按回车键退出...")