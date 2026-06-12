import os
import glob
from pathlib import Path

# ============ 配置路径 ============
# ROOT = Path(r"D:\Data\20260416\OVH9000_DCG_20260416\ace_pro2")
ROOT = Path(r"D:\Data\20260417\ace_pro2")

IMU_PATH = ROOT / "mp4" / "imu"
GYRO_DATA_PATH = ROOT / "gyro_data"

# ============ 主处理逻辑 ============
def process_gyro_files():
    """处理所有 gyro.std.txt 文件并生成 CSV"""
    
    # 1. 创建输出目录
    os.makedirs(GYRO_DATA_PATH, exist_ok=True)
    print(f"输入路径: {IMU_PATH}")
    print(f"输出路径: {GYRO_DATA_PATH}")
    print("=" * 60)
    
    # 2. 获取所有 gyro.std.txt 文件
    gyro_files = glob.glob(os.path.join(IMU_PATH, '*.mp4.gyro.std.txt'))
    gyro_files.sort()
    
    print(f"找到 {len(gyro_files)} 个 gyro 文件")
    print("=" * 60)
    
    if not gyro_files:
        print("未找到任何 gyro 文件！")
        return
    
    # 3. 处理每个文件
    success_count = 0
    failed_count = 0
    
    for file_in in gyro_files:
        try:
            # 提取文件名（不含路径）
            filename = os.path.basename(file_in)
            # 移除 .mp4.gyro.std.txt 后缀，获取基础名称
            # 例如: 00__outdoor_1234_10ms_door.mp4.gyro.std.txt -> 00__outdoor_1234_10ms_door
            base_name = filename.replace('.mp4.gyro.std.txt', '')
            
            # 生成输出文件名
            file_out = os.path.join(GYRO_DATA_PATH, f'{base_name}__gyro_data.csv')
            
            # 读取并处理文件
            with open(file_in, 'r') as f:
                lines = f.readlines()
            
            # 写入 CSV 文件
            with open(file_out, 'w') as f:
                # 写入表头
                f.write('ts(ns),gyro_x(rad/s),gyro_y(rad/s),gyro_z(rad/s),\n')
                
                # 处理每一行数据
                for line in lines:
                    line = line.strip()
                    if not line:  # 跳过空行
                        continue
                    
                    text = line.split('_')
                    # 提取需要的字段: [timestamp, _, _, _, gyro_x, gyro_y, gyro_z]
                    v = [float(text[i].strip()) for i in [0, 4, 5, 6]]
                    
                    # 写入 CSV 行: 时间戳转换为 ns，陀螺仪数据保持 rad/s
                    f.write(f'{int(v[0]*1000)},{v[1]},{v[2]},{v[3]}\n')
            
            print(f"✓ {filename}")
            success_count += 1
            
        except Exception as e:
            print(f"✗ {filename} - 错误: {e}")
            failed_count += 1
    
    # 4. 统计结果
    print("\n" + "=" * 60)
    print(f"处理完成！")
    print(f"成功: {success_count} 个文件")
    if failed_count > 0:
        print(f"失败: {failed_count} 个文件")
    print("=" * 60)

if __name__ == "__main__":
    # 检查输入路径是否存在
    if not os.path.exists(IMU_PATH):
        print(f"错误：输入路径不存在: {IMU_PATH}")
    else:
        process_gyro_files()