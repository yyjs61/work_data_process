import os
import shutil

def process_scenes(base_path):
    """
    遍历 base_path 下的所有子文件夹（场景），
    将每个场景下 'raw' 文件夹内的文件移动到场景根目录。
    """
    if not os.path.exists(base_path):
        print(f"错误：找不到路径 {base_path}")
        return

    # 获取 base_path 下的所有直接子目录（即场景文件夹）
    try:
        scene_dirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    except PermissionError:
        print("权限错误，无法读取目录。")
        return

    print(f"检测到 {len(scene_dirs)} 个场景文件夹，开始处理...\n")

    total_moved = 0

    for scene_name in scene_dirs:
        scene_path = os.path.join(base_path, scene_name)
        raw_folder_path = os.path.join(scene_path, 'raw')

        # 1. 检查是否存在 raw 文件夹
        if os.path.exists(raw_folder_path) and os.path.isdir(raw_folder_path):
            print(f"[处理] 场景: {scene_name}")
            
            # 获取 raw 文件夹下的所有项目
            items = os.listdir(raw_folder_path)
            moved_count = 0

            for item_name in items:
                src_path = os.path.join(raw_folder_path, item_name)
                dst_path = os.path.join(scene_path, item_name)

                # 确保只移动文件，防止误移动子文件夹
                if os.path.isfile(src_path):
                    try:
                        shutil.move(src_path, dst_path)
                        moved_count += 1
                    except Exception as e:
                        print(f"  ! 移动失败 {item_name}: {e}")
                elif os.path.isdir(src_path):
                    # 如果 raw 里面还有文件夹，可以选择递归移动或者跳过，这里选择跳过并提示
                    print(f"  - 跳过子文件夹: {item_name}")

            print(f"  -> 成功移动 {moved_count} 个文件到场景根目录")
            total_moved += moved_count

            # 2. 清理工作：如果 raw 文件夹空了，将其删除
            if not os.listdir(raw_folder_path):
                try:
                    os.rmdir(raw_folder_path)
                    # print(f"  -> 已删除空的 raw 文件夹")
                except OSError:
                    pass # 忽略删除失败（通常是因为非空，虽然上面判断了）
        else:
            # 如果某个场景下没有 raw 文件夹，可以选择打印或忽略
            # print(f"[跳过] 场景 {scene_name} 下未找到 raw 文件夹")
            pass

    print(f"\n--- 处理完成 ---")
    print(f"总共移动了 {total_moved} 个文件。")

if __name__ == "__main__":
    # 根据你的截图，设置基础路径
    # 注意：Windows路径建议在字符串前加 r 以避免转义字符问题
    target_root = r"D:\Data\DJI_OV50X\20260509\data2\received"
    
    process_scenes(target_root)
    
    # 防止脚本运行完立刻关闭窗口（如果是直接双击运行）
    input("\n按回车键退出...")