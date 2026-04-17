import ctypes
import glob
import os
import re
import numpy as np
import shutil
import datetime

def rawPreprocess(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth, in_filepath, out_filepath):
    """
    调用 DLL 进行 RAW 数据 unpack
    """
    lib = ctypes.cdll.LoadLibrary('./OV50X/libSequentialUnpacker.dll')
    in_filepath_c_str = ctypes.c_char_p(bytes(in_filepath, 'utf-8'))
    out_filepath_c_str = ctypes.c_char_p(bytes(out_filepath, 'utf-8'))
    lib.sequentialUnpacker(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth,
                           in_filepath_c_str, out_filepath_c_str)

def add_suffix_based_on_port(filename):
    """
    根据文件名中的 port[数字] 添加后缀
    port[2] -> 添加 __short
    port[9] -> 添加 __long
    """
    # 分离文件名和扩展名
    base_name, ext = os.path.splitext(filename)
    
    # 检查是否包含 _port[2]_ 或 _port[9]_
    if '_port[2]_' in base_name:
        new_base_name = base_name + '__short'
        print(f"  [短曝光] 添加 __short 后缀")
    elif '_port[9]_' in base_name:
        new_base_name = base_name + '__long'
        print(f"  [长曝光] 添加 __long 后缀")
    else:
        # 如果没有匹配的 port，保持原样
        new_base_name = base_name
        print(f"  [未知 port] 不添加后缀")

    return new_base_name + ext

def is_short_exposure(filename):
    """
    判断文件是否为短曝光文件
    条件：文件名包含 'port[2]' 或 '__short'
    """
    base_name, _ = os.path.splitext(filename)
    if '_port[2]_' in base_name or '__short' in base_name:
        return True
    return False

def shift_raw_right(filepath, shift_bits=2, dtype=np.uint16):
    """
    将 RAW 文件数据右移指定比特位
    """
    try:
        # 读取二进制数据
        data = np.fromfile(filepath, dtype=dtype)
        
        if data.size == 0:
            print(f"    [警告] 文件为空，跳过右移")
            return False
        
        # 执行右移
        data_shifted = data >> shift_bits
        
        # 写回文件（覆盖）
        data_shifted.tofile(filepath)
        
        return True
    except Exception as e:
        print(f"    [错误] 右移失败：{e}")
        return False

# def backup_unpack_raw(root_dir, tag):
    """
    备份 unpack_raw 目录
    """
    unpack_dir = os.path.join(root_dir, tag)
    if not os.path.exists(unpack_dir):
        return None
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"{unpack_dir}_backup_{timestamp}"
    
    print(f"\n正在备份 {tag} 目录至：{backup_dir} ...")
    try:
        shutil.copytree(unpack_dir, backup_dir)
        print(f"备份完成。")
        return backup_dir
    except Exception as e:
        print(f"警告：备份失败 ({e})")
        return None

if __name__ == '__main__':
    height = 3072
    width = 4096
    stride = 7168
    in_pack_bit_depth = 14
    out_unpack_bit_depth = 14
    
    # ROOT = r'C:\Users\admin.DESKTOP-QNCO006\Desktop\Data\OV50X_DCGandLOFIC_20260401__night_hdr'
    ROOT = r'C:\Users\admin.DESKTOP-QNCO006\Desktop\Data\OV50X\OV50X_DCGandLOFIC_20260410__lab_ipad'
    RECEIVED = os.path.join(ROOT, "received")
    tag = 'unpack_raw'
    
    scenes = glob.glob(os.path.join(RECEIVED, '*'))
    print(f"源目录：{RECEIVED}")
    print(f"场景数量：{len(scenes)}")
    
    os.makedirs(os.path.join(ROOT, tag), exist_ok=True)

    # 统计信息
    count_unpack = 0
    count_shift = 0
    count_skip = 0
    count_errors = 0

    for scene in sorted(scenes):
        scene_name = os.path.basename(scene)
        out_scene_dir = os.path.join(ROOT, tag, scene_name)
        os.makedirs(out_scene_dir, exist_ok=True)
        
        file_tag = '*.raw'
        file_paths = sorted(glob.glob(os.path.join(scene, file_tag)))
        
        print(f"\n{'='*60}")
        print(f"处理场景：{scene_name}")
        print(f"文件数量：{len(file_paths)}")
        print(f"{'='*60}")
        
        for file_path in file_paths:
            if os.path.getsize(file_path) == 0:
                print(f'  {os.path.basename(file_path)}: 数据大小为 0，跳过')
                count_skip += 1
                continue
            
            filename = os.path.basename(file_path)
            
            # 根据 port 添加后缀
            new_filename = add_suffix_based_on_port(filename)
            out_path = os.path.join(ROOT, tag, scene_name, new_filename)
            
            # print(f'\n  [Unpack] {filename} -> {new_filename}')
            
            try:
                # 1. 执行 unpack
                rawPreprocess(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth,
                             file_path, out_path)
                count_unpack += 1
                
                # 2. 判断是否为短曝光文件，如果是则右移 2 位
                if is_short_exposure(new_filename):
                    # print(f'  [Shift] 检测到短曝光文件，执行右移 2 位...')
                    if shift_raw_right(out_path, shift_bits=2, dtype=np.uint16):
                        print(f'  [成功] 右移完成')
                        count_shift += 1
                    else:
                        print(f'  [失败] 右移出错')
                        count_errors += 1
                else:
                    print(f'  [跳过] 非短曝光文件，不需右移')
                    
            except Exception as e:
                print(f'  [错误] 处理失败：{e}')
                count_errors += 1

    print(f"\n{'='*60}")
    print(f"全部处理完成")
    print(f"{'='*60}")
    print(f"Unpack 文件数：{count_unpack}")
    print(f"右移文件数：{count_shift}")
    print(f"跳过文件数：{count_skip}")
    print(f"错误文件数：{count_errors}")
    
    # 提示备份
    print(f"\n提示：unpack_raw 目录已包含处理后的数据")
    print(f"如需恢复原始 unpack 数据，请在运行前手动备份")
    
    input("\n按回车键退出...")