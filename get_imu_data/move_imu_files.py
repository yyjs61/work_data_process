import os
import shutil
from pathlib import Path

# ============ 配置变量 ============
# 基础路径
# BASE_PATH = r"D:\Data\20260416\OVH9000_DCG_20260416\ace_pro2"
BASE_PATH = r"D:\Data\20260417\ace_pro2"

# MP4 文件夹路径
MP4_FOLDER = os.path.join(BASE_PATH, "mp4")

# IMU 文件夹路径（存放非 mp4 文件）
IMU_FOLDER = os.path.join(MP4_FOLDER, "imu")

# ============ 主处理逻辑 ============
def move_non_mp4_files():
    """将 mp4 文件夹下所有非 .mp4 文件移动到 imu 子文件夹"""
    
    # 1. 创建 imu 文件夹（如果不存在）
    os.makedirs(IMU_FOLDER, exist_ok=True)
    print(f"IMU 文件夹路径: {IMU_FOLDER}")
    print("-" * 60)
    
    # 2. 获取 mp4 文件夹下的所有文件（不包括子文件夹）
    all_files = [f for f in os.listdir(MP4_FOLDER) 
                 if os.path.isfile(os.path.join(MP4_FOLDER, f))]
    
    # 3. 过滤出非 .mp4 文件
    non_mp4_files = [f for f in all_files if not f.lower().endswith('.mp4')]
    
    print(f"找到 {len(all_files)} 个文件")
    print(f"其中 {len(non_mp4_files)} 个非 MP4 文件需要移动")
    print("-" * 60)
    
    if not non_mp4_files:
        print("没有需要移动的文件")
        return
    
    # 4. 移动文件
    moved_count = 0
    failed_count = 0
    
    for filename in non_mp4_files:
        src_path = os.path.join(MP4_FOLDER, filename)
        dst_path = os.path.join(IMU_FOLDER, filename)
        
        try:
            # 如果目标文件已存在，添加序号避免覆盖
            if os.path.exists(dst_path):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(dst_path):
                    new_filename = f"{base}_{counter}{ext}"
                    dst_path = os.path.join(IMU_FOLDER, new_filename)
                    counter += 1
            
            shutil.move(src_path, dst_path)
            print(f"✓ {filename}")
            moved_count += 1
        except Exception as e:
            print(f"✗ {filename} - 错误: {e}")
            failed_count += 1
    
    # 5. 统计结果
    print("\n" + "=" * 60)
    print(f"移动完成！")
    print(f"成功移动: {moved_count} 个文件")
    if failed_count > 0:
        print(f"失败: {failed_count} 个文件")
    print("=" * 60)

if __name__ == "__main__":
    # 检查路径是否存在
    if not os.path.exists(MP4_FOLDER):
        print(f"错误：路径不存在: {MP4_FOLDER}")
    else:
        print(f"基础路径: {BASE_PATH}")
        print(f"MP4 文件夹: {MP4_FOLDER}")
        print("-" * 60)
        
        # 显示将要移动的文件类型统计
        all_files = [f for f in os.listdir(MP4_FOLDER) 
                     if os.path.isfile(os.path.join(MP4_FOLDER, f))]
        non_mp4_files = [f for f in all_files if not f.lower().endswith('.mp4')]
        
        if non_mp4_files:
            # 统计文件扩展名
            ext_count = {}
            for f in non_mp4_files:
                ext = os.path.splitext(f)[1] or "无扩展名"
                ext_count[ext] = ext_count.get(ext, 0) + 1
            
            print("将要移动的文件类型:")
            for ext, count in sorted(ext_count.items()):
                print(f"  {ext}: {count} 个")
            print("-" * 60)
        
        # 确认操作
        response = input("是否继续执行移动操作？(y/n): ")
        if response.lower() == 'y':
            move_non_mp4_files()
        else:
            print("操作已取消")