import os
import glob
import shutil
import natsort

def process_isp_raws():
    # ================= 配置区域 =================
    # 请根据实际路径修改 ROOT
    # 参考你之前的截图，路径可能是 E 盘
    # ROOT = r"D:\Data\2026_05\20\Test_data_260520\IMX678_Test_data_260520"
    ROOT = r"D:\Data\2026_05\21\IMX678_Test_data_260521"
    
    RECEIVED_DIR = os.path.join(ROOT, 'received')
    UNPACK_RAW_DIR = os.path.join(ROOT, 'unpack_raw')
    # =============================================

    if not os.path.exists(RECEIVED_DIR):
        print(f"错误：找不到源目录 {RECEIVED_DIR}")
        return

    # 创建目标根目录
    os.makedirs(UNPACK_RAW_DIR, exist_ok=True)

    # 1. 获取所有场景文件夹，并使用 natsort 进行自然排序
    # 过滤掉非文件夹项
    scenes = [f for f in os.listdir(RECEIVED_DIR) if os.path.isdir(os.path.join(RECEIVED_DIR, f))]
    scenes = natsort.natsorted(scenes)

    print(f"发现 {len(scenes)} 个场景，开始处理...")

    for scene_idx, scene_name in enumerate(scenes):
        src_scene_path = os.path.join(RECEIVED_DIR, scene_name)
        
        # 目标场景名格式：00__SceneName
        dst_scene_name = f"{scene_idx:02d}__{scene_name}"
        dst_scene_path = os.path.join(UNPACK_RAW_DIR, dst_scene_name)
        os.makedirs(dst_scene_path, exist_ok=True)

        # 2. 获取该场景下的所有 raw 文件
        raw_files = glob.glob(os.path.join(src_scene_path, '*.raw'))
        
        # 分离 Long 和 Short 文件
        long_files = []
        short_files = []
        other_files = [] # 备用，处理没有标记的文件

        for f in raw_files:
            basename = os.path.basename(f)
            if '__long' in basename:
                long_files.append(f)
            elif '__short' in basename:
                short_files.append(f)
            else:
                other_files.append(f)

        # 3. 分别对 Long 和 Short 进行自然排序
        long_files = natsort.natsorted(long_files)
        short_files = natsort.natsorted(short_files)
        other_files = natsort.natsorted(other_files)

        # 4. 合并文件列表以实现交错排序 (Long, Short, Long, Short...)
        # 这样可以保证 Long 在偶数索引 (0, 2...)，Short 在奇数索引 (1, 3...)
        merged_files = []
        max_len = max(len(long_files), len(short_files))

        for i in range(max_len):
            if i < len(long_files):
                merged_files.append(long_files[i])
            if i < len(short_files):
                merged_files.append(short_files[i])
        
        # 将没有标记的文件追加到最后（可选）
        merged_files.extend(other_files)

        # 5. 拷贝并重命名
        print(f"\n处理场景：{scene_name} -> {dst_scene_name}")
        for file_idx, src_file in enumerate(merged_files):
            # 生成前缀：000__, 001__, ...
            prefix = f"{file_idx:03d}__"
            src_basename = os.path.basename(src_file)
            dst_filename = prefix + src_basename
            
            dst_file_path = os.path.join(dst_scene_path, dst_filename)
            
            try:
                # 使用 copy2 保留元数据，如果是 move 请改为 shutil.move
                shutil.copy2(src_file, dst_file_path)
                # print(f"  [OK] {src_basename} -> {dst_filename}")
            except Exception as e:
                print(f"  [Error] 拷贝失败 {src_basename}: {e}")

        print(f"  -> 完成。共处理 {len(merged_files)} 个文件 (Long: {len(long_files)}, Short: {len(short_files)})")

    print("\n所有场景处理完毕！")

if __name__ == "__main__":
    process_isp_raws()