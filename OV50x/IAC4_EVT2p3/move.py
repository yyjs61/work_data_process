import ctypes
import glob
import os
import sys
from natsort import natsorted  # 需要安装 natsort

def rawPreprocess(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth, in_filepath, out_filepath):
    # lib = ctypes.cdll.LoadLibrary('libSequentialUnpacker.so')
    # lib = ctypes.cdll.LoadLibrary('/home/user/Tools_App/data_process_demo-main/Sequential_unpacked/libSequentialUnpacker.so')
    lib = ctypes.windll.LoadLibrary('./libSequentialUnpacker.dll')  # use this if run on Win64
    in_filepath_c_str = ctypes.c_char_p(bytes(in_filepath, 'utf-8'))
    out_filepath_c_str = ctypes.c_char_p(bytes(out_filepath, 'utf-8'))
    lib.sequentialUnpacker(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth, in_filepath_c_str, out_filepath_c_str)

def postprocess_unpacked(unpack_root):
    """
    对 unpack_root 目录下的子场景及场景内的 raw 文件进行重命名：
    - 子场景添加两位数字前缀（如 00__场景名）
    - 场景内的 .raw 文件添加三位数字前缀（如 000__原文件名.raw）
    """
    if not os.path.isdir(unpack_root):
        print(f"错误：{unpack_root} 目录不存在，跳过后处理。")
        return

    # 获取所有子目录（场景文件夹）
    all_items = os.listdir(unpack_root)
    scene_dirs = [item for item in all_items if os.path.isdir(os.path.join(unpack_root, item))]
    if not scene_dirs:
        print("未找到任何场景文件夹，跳过重命名。")
        return

    # 自然排序
    sorted_scenes = natsorted(scene_dirs)
    print(f"\n开始后处理：为 {len(sorted_scenes)} 个场景文件夹添加前缀...")

    for idx, scene_name in enumerate(sorted_scenes):
        old_path = os.path.join(unpack_root, scene_name)
        new_name = f"{idx:02d}__{scene_name}"
        new_path = os.path.join(unpack_root, new_name)

        # 如果新路径已存在且不是同一个目录，则跳过
        if os.path.exists(new_path) and new_path != old_path:
            print(f"  警告：目标文件夹 '{new_name}' 已存在，跳过重命名 '{scene_name}'。")
            # 仍然处理该文件夹下的 raw 文件（使用旧路径）
            process_raw_files(old_path)
            continue

        # 重命名场景文件夹
        print(f"  重命名场景：'{scene_name}' -> '{new_name}'")
        os.rename(old_path, new_path)
        # 处理重命名后的文件夹内的 raw 文件
        process_raw_files(new_path)

def process_raw_files(folder_path):
    """处理指定文件夹内的所有 .raw 文件，添加三位数字前缀"""
    if not os.path.isdir(folder_path):
        return

    # 收集所有 .raw 文件
    raw_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.raw')]
    if not raw_files:
        print(f"    在 '{os.path.basename(folder_path)}' 中未找到 .raw 文件。")
        return

    # 自然排序
    sorted_raw = natsorted(raw_files)
    print(f"    找到 {len(sorted_raw)} 个 .raw 文件，开始添加前缀...")

    for i, old_name in enumerate(sorted_raw):
        new_name = f"{i:03d}__{old_name}"
        old_path = os.path.join(folder_path, old_name)
        new_path = os.path.join(folder_path, new_name)

        # 如果目标文件已存在且不是同一个文件，则跳过
        if os.path.exists(new_path) and old_path != new_path:
            print(f"      警告：目标文件 '{new_name}' 已存在，跳过 '{old_name}'。")
            continue

        os.rename(old_path, new_path)
        print(f"      重命名：'{old_name}' -> '{new_name}'")

if __name__ == '__main__':
    # 解包参数（根据实际相机配置调整）
    # height = 4912
    # width = 8192
    # stride = 10240
    height = 4096
    width = 4096
    stride = 5120
    in_pack_bit_depth = 10
    out_unpack_bit_depth = 10

    # 定义根目录（请根据实际路径修改）
    ROOT = r'C:\Users\admin.DESKTOP-QNCO006\Desktop\IAC4\IAC4_EVT2p3_QUAD_Wide_20260420'

    # 输入目录：received 文件夹（存放原始 camera_* 场景）
    input_dir = os.path.join(ROOT, 'received')
    # 输出目录：unpack_raw 文件夹（与 received 并列）
    output_root = os.path.join(ROOT, 'unpack_raw')

    # 检查输入目录是否存在
    if not os.path.isdir(input_dir):
        print(f"错误：输入目录 '{input_dir}' 不存在。")
        sys.exit(1)

    # 创建输出根目录
    os.makedirs(output_root, exist_ok=True)

    # 获取所有原始场景文件夹（camera_*）
    # scenes = glob.glob(os.path.join(input_dir, 'camera_*'))
    scenes = glob.glob(os.path.join(input_dir, 'data_raw_*'))
    if not scenes:
        print(f"在 '{input_dir}' 下未找到 camera_* 文件夹，请检查路径。")
        sys.exit(1)

    print(f"找到 {len(scenes)} 个场景文件夹，开始解包...")

    # 解包处理
    for scene in sorted(scenes):
        scene_name = os.path.basename(scene)
        output_scene_dir = os.path.join(output_root, scene_name)
        os.makedirs(output_scene_dir, exist_ok=True)

        # 获取当前场景下的所有 .raw 文件
        file_paths = sorted(glob.glob(os.path.join(scene, '*.raw')))
        print(f"  处理场景：{scene_name}，共 {len(file_paths)} 个 raw 文件")
        for file_path in file_paths:
            # 输出文件名：原文件名 + __unpacked.raw
            out_filename = os.path.basename(file_path).replace('.raw', '__unpacked.raw')
            out_path = os.path.join(output_scene_dir, out_filename)

            # 调用解包函数
            rawPreprocess(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth,
                          file_path, out_path)

    print("\n解包完成，开始后处理（添加数字前缀）...")

    # 后处理：为输出目录中的场景和 raw 文件添加递增前缀
    postprocess_unpacked(output_root)

    print("\n所有操作完成！")