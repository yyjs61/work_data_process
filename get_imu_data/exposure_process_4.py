import os
import glob
import json
import re
from pathlib import Path

# ============ 配置路径 ============
ROOT = Path(r"D:\Data\20260417\ace_pro2")
IMU_PATH = ROOT / "mp4" / "imu"
RECEIVED_PATH = ROOT / "received"
GYRO_DATA_PATH = ROOT / "gyro_data"

# 创建输出目录
os.makedirs(GYRO_DATA_PATH, exist_ok=True)

N_IMGS_PER_FILE = 50

def parseLine(line):
    """解析包含方括号的行，提取数值"""
    try:
        values = line.split('[')[1:]
        values = [v.split(']')[0] for v in values]
        values = [float(v) if '.' in v else int(v) for v in values]
        return values
    except Exception:
        return None

def extract_scene_and_video_name(json_filename):
    """
    从 JSON 文件名中提取场景名和视频名
    例如：00__inner_ISO100_33ms_00__brush.mp4.metadata.json
    返回：scene_name='inner_ISO100_33ms', video_name='00__brush'
    """
    try:
        # 去掉后缀 .mp4.metadata.json
        base_name = json_filename.replace('.mp4.metadata.json', '')
        
        # 格式：{prefix}__{scene_name}_{video_index}__{video_name}
        # 例如：00__inner_ISO100_33ms_00__brush
        
        # 使用正则表达式匹配
        # 匹配模式：数字__ + 场景名 + _ + 数字__ + 视频名
        match = re.match(r'(\d+)__([A-Za-z0-9_]+)_(\d+)__(.+)', base_name)
        
        if match:
            prefix = match.group(1)          # 00
            scene_name = match.group(2)       # inner_ISO100_33ms
            video_index = match.group(3)      # 00
            video_name_part = match.group(4)  # brush
            
            # 组合成完整的视频名：00__brush
            video_name = f"{video_index}__{video_name_part}"
            
            return scene_name, video_name
        else:
            print(f"  [警告] 无法解析文件名格式: {json_filename}")
            return None, None
    except Exception as e:
        print(f"  [错误] 解析文件名失败: {e}")
        return None, None

def main():
    print("=" * 60)
    print("Exposure Timestamp 处理程序")
    print(f"输入 IMU 路径: {IMU_PATH}")
    print(f"输入 Received 路径: {RECEIVED_PATH}")
    print(f"输出 Gyro Data 路径: {GYRO_DATA_PATH}")
    print("=" * 60)

    # 1. 在 mp4/imu 下找到所有 *.mp4.metadata.json 文件
    json_files = list(IMU_PATH.glob("*.mp4.metadata.json"))
    
    # 排序以保证处理顺序一致
    json_files.sort()
    
    if not json_files:
        print(f"错误：未在 IMU 路径下找到任何 JSON 文件 -> {IMU_PATH}")
        return

    print(f"找到 {len(json_files)} 个 JSON 文件。开始处理...\n")

    success_count = 0
    fail_count = 0

    for json_path in json_files:
        json_filename = json_path.name
        print(f"处理 JSON: {json_filename}")
        
        # 2. 从文件名提取场景名和视频名
        scene_name, video_name = extract_scene_and_video_name(json_filename)
        
        if not scene_name or not video_name:
            print(f"  [跳过] 无法从文件名提取场景名或视频名")
            fail_count += 1
            continue
        
        print(f"  -> 场景名: {scene_name}")
        print(f"  -> 视频名: {video_name}")

        # 3. 构建 txt 文件路径
        # 路径格式: received/{scene_name}/{video_name}/raw_dump_*.txt
        # 例如: received/inner_ISO100_33ms/00__brush/raw_dump_0.txt
        txt_dir = RECEIVED_PATH / scene_name / video_name
        
        if not txt_dir.is_dir():
            print(f"  [跳过] 找不到目录: {txt_dir}")
            fail_count += 1
            continue

        # 查找 txt 文件
        txt_files = list(txt_dir.glob("raw_dump_*.txt"))
        if not txt_files:
            print(f"  [跳过] 在 {txt_dir} 下未找到 raw_dump_*.txt 文件")
            fail_count += 1
            continue
            
        txt_path = txt_files[0]  # 使用第一个找到的 txt 文件
        print(f"  -> 找到 TXT: {txt_path.relative_to(RECEIVED_PATH)}")

        try:
            # 4. 读取 JSON 获取 rolling_shutter_time
            with open(json_path, "r", encoding="utf-8") as file:
                json_data = json.load(file)
            
            if 'rolling_shutter_time' not in json_data:
                print(f"  [错误] JSON 中缺少 rolling_shutter_time 字段")
                fail_count += 1
                continue

            frame_readout_time = json_data['rolling_shutter_time'] * 1000000

            # 5. 读取 TXT 文件
            with open(txt_path, 'r') as fi:
                lines = fi.readlines()
            
            # 6. 生成输出 CSV 文件
            # 使用原 JSON 文件名作为基础
            output_filename = json_filename.replace('.mp4.metadata.json', '__exposure_timestamp.csv')
            output_path = GYRO_DATA_PATH / output_filename

            print(f"  -> 生成 CSV: {output_filename}")

            with open(output_path, 'w') as file:
                file.write('frame_id,long_expo_start_time,long_expo_time,frame_readout_time,\n')

                for i in range(N_IMGS_PER_FILE):
                    # 确保行数足够
                    if 2*i >= len(lines) or (2 * N_IMGS_PER_FILE + i) >= len(lines):
                        break
                        
                    line_AE = lines[2*i]
                    if not line_AE.startswith('AEINFO'):
                        continue 
                        
                    try:
                        parsed_AE = parseLine(line_AE)
                        if parsed_AE is None: continue
                        
                        f, s, _, _, _ = parsed_AE
                        long_expo_time = int(s * 1000000)
                        frame_id = f

                        line_gyro = lines[2 * N_IMGS_PER_FILE + i]
                        if not line_gyro.startswith('GYRO'):
                            continue

                        parsed_gyro = parseLine(line_gyro)
                        if parsed_gyro is None: continue
                        
                        f_gyro, long_expo_start_time, _, _, _, _, _, _ = parsed_gyro

                        if frame_id == f_gyro:
                            long_expo_start_time *= 1000
                            # 计算公式
                            long_expo_start_time = long_expo_start_time - long_expo_time - frame_readout_time
                            
                            file.write(f'{frame_id},{long_expo_start_time},{long_expo_time},{frame_readout_time}\n')
                    except Exception as e:
                        print(f"  [警告] 解析数据行失败: {e}")
                        continue

            print(f"  [成功] 处理完毕\n")
            success_count += 1

        except Exception as e:
            print(f"  [错误] 处理过程中发生异常: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1

    print("=" * 60)
    print(f"全部任务完成。成功: {success_count}, 失败/跳过: {fail_count}")
    print("=" * 60)

if __name__ == "__main__":
    main()