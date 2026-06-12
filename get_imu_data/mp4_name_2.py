import os
import shutil
from pathlib import Path

# ============ 配置路径 ============
BASE_PATH = r"D:\Data\20260417\OVH9000_DCG_20260417_low_light\ace_pro2"
# BASE_PATH = r"D:\Data\20260417\honor"

MP4_FOLDER = os.path.join(BASE_PATH, "mp4")

# ============ 主处理逻辑 ============
def process_videos():
    """处理所有场景文件夹中的视频文件"""
    
    # 获取所有子文件夹（场景）
    scene_folders = [f for f in os.listdir(MP4_FOLDER) 
                     if os.path.isdir(os.path.join(MP4_FOLDER, f))]
    
    # 按自然排序（如果需要）
    scene_folders.sort()
    
    print(f"找到 {len(scene_folders)} 个场景文件夹")
    print("-" * 60)
    
    # 全局计数器（用于生成序号）
    global_counter = 0
    
    # 遍历每个场景文件夹
    for scene_name in scene_folders:
        scene_path = os.path.join(MP4_FOLDER, scene_name)
        print(f"\n处理场景: {scene_name}")
        
        # 获取该场景下的所有 MP4 文件
        mp4_files = [f for f in os.listdir(scene_path) 
                     if f.lower().endswith('.mp4')]
        mp4_files.sort()  # 排序确保顺序一致
        
        print(f"  找到 {len(mp4_files)} 个视频文件")
        
        # 处理每个视频文件
        for video_file in mp4_files:
            # 生成新文件名
            new_filename = f"{str(global_counter).zfill(2)}__{scene_name}_{video_file}"
            src_path = os.path.join(scene_path, video_file)
            dst_path = os.path.join(MP4_FOLDER, new_filename)
            
            # 移动并重命名文件
            try:
                shutil.move(src_path, dst_path)
                print(f"  ✓ {video_file} -> {new_filename}")
                global_counter += 1
            except Exception as e:
                print(f"  ✗ 移动失败: {video_file}, 错误: {e}")
        
        # 删除空的场景文件夹
        try:
            if not os.listdir(scene_path):  # 如果文件夹为空
                os.rmdir(scene_path)
                print(f"  已删除空文件夹: {scene_name}")
        except Exception as e:
            print(f"  删除文件夹失败: {scene_name}, 错误: {e}")
    
    print("\n" + "=" * 60)
    print(f"处理完成！共移动 {global_counter} 个视频文件")
    print("=" * 60)

if __name__ == "__main__":
    # 检查路径是否存在
    if not os.path.exists(MP4_FOLDER):
        print(f"错误：路径不存在: {MP4_FOLDER}")
    else:
        print(f"基础路径: {BASE_PATH}")
        print(f"MP4 文件夹: {MP4_FOLDER}")
        print("-" * 60)
        
        # 确认操作
        response = input("是否继续执行移动操作？(y/n): ")
        if response.lower() == 'y':
            process_videos()
        else:
            print("操作已取消")