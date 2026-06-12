import os
import sys

def rename_files_by_prefix(root_dir):
    # 1. 检查目录是否存在
    if not os.path.exists(root_dir):
        print(f"错误：目录不存在 -> {root_dir}")
        return

    if not os.path.isdir(root_dir):
        print(f"错误：路径不是一个目录 -> {root_dir}")
        return

    print(f"开始处理目录：{root_dir}")
    print("-" * 50)

    count_success = 0
    count_skip = 0
    count_conflict = 0

    # 2. 获取目录下所有文件
    try:
        files = os.listdir(root_dir)
    except PermissionError:
        print("错误：没有权限访问该目录")
        return

    # 3. 遍历文件
    for filename in files:
        old_path = os.path.join(root_dir, filename)
        
        # 只处理文件，跳过子文件夹
        if not os.path.isfile(old_path):
            continue

        # 分离文件名和扩展名
        name, ext = os.path.splitext(filename)
        
        # 4. 提取前缀序号 (取第一个下划线之前的内容)
        if '_' in name:
            prefix = name.split('_')[0]
            new_filename = f"{prefix}{ext}"
        else:
            # 如果文件名中没有下划线，保持原名（或者你可以选择跳过）
            continue 

        new_path = os.path.join(root_dir, new_filename)

        # 5. 判断是否需要重命名
        if filename == new_filename:
            count_skip += 1
            continue

        # 6. 检查目标文件是否已存在 (防止覆盖)
        if os.path.exists(new_path):
            print(f"[冲突] 跳过：'{filename}' -> '{new_filename}' (目标文件已存在)")
            count_conflict += 1
            continue

        # 7. 执行重命名
        try:
            os.rename(old_path, new_path)
            print(f"[成功] 重命名：'{filename}' -> '{new_filename}'")
            count_success += 1
        except Exception as e:
            print(f"[失败] 重命名：'{filename}' 出错：{e}")

    print("-" * 50)
    print(f"处理完成。成功：{count_success}, 跳过 (无需修改)：{count_skip}, 跳过 (名称冲突)：{count_conflict}")

if __name__ == "__main__":
    # 设置根目录
    # ROOT = r"D:\Data\20260420\DRC_20260420"
    # ROOT = r"D:\Data\2026_05\08\00__1_IMX832_WDR_DoL_ratio32_LEF4ms_0dB_backlight_v2_0508_20bit"
    ROOT = r"D:\Data\2026_06\05\06__260521_IMX678_60dB_30ms_0p5lux"
    
    # 执行重命名函数
    rename_files_by_prefix(ROOT)
    
    # 防止脚本运行完后窗口立即关闭 (如果是直接双击运行)
    input("\n按回车键退出...")