#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISP Raw数据批量解包预处理脚本
功能：遍历received下的场景文件夹，将.RAWMIPI10文件解包并输出到unpack_raw目录
"""
import os
import glob
import ctypes
import sys

def rawPreprocess(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth, in_filepath, out_filepath):
    """调用C++解包DLL/SO"""
    # 根据操作系统自动选择动态库类型
    if os.name == 'nt':  # Windows
        lib_path = './IAC4/libSequentialUnpacker.dll'
        lib = ctypes.windll.LoadLibrary(lib_path)
    else:  # Linux / macOS
        lib_path = './Calibration/libSequentialUnpacker.so'
        lib = ctypes.cdll.LoadLibrary(lib_path)
    
    # 转换Python字符串为C兼容的字节指针
    in_filepath_c_str = ctypes.c_char_p(in_filepath.encode('utf-8'))
    out_filepath_c_str = ctypes.c_char_p(out_filepath.encode('utf-8'))
    
    # 调用C接口
    lib.sequentialUnpacker(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth, 
                          in_filepath_c_str, out_filepath_c_str)

def process_all_scenes():
    # ================= 配置区 =================
    # BASE_ROOT = '/home/user/afs_data/202605/22/F_CAPCRQO_HEX_20260522'
    # BASE_ROOT = r'D:\Data\2026_05\22\IAC4_IMX01F_DCG_ER4_UltralWide_20260522'
    BASE_ROOT = r'D:\Data\2026_06\07\IAC4_IMX01F_DCG_ER4_Wide_move_20260608'

    RECEIVED_ROOT = os.path.join(BASE_ROOT, 'received')
    UNPACK_RAW_ROOT = os.path.join(BASE_ROOT, 'unpack_raw')
    
    # 解包参数 (可根据实际Sensor规格或从meta/txt中动态解析修改)
    PARAMS = {
        'height': 3600,
        'width': 4096,
        'stride': 6144,
        'in_bit': 12,        # RAWMIPI10 输入为10bit
        'out_bit': 12        
    }
    # ==========================================
    
    if not os.path.exists(RECEIVED_ROOT):
        print(f"[错误] 源目录不存在: {RECEIVED_ROOT}")
        sys.exit(1)
    
    # 确保目标目录存在
    os.makedirs(UNPACK_RAW_ROOT, exist_ok=True)
    
    print(f"{'='*60}")
    print(f"源目录: {RECEIVED_ROOT}")
    print(f"目标目录: {UNPACK_RAW_ROOT}")
    print(f"{'='*60}")
    
    # 遍历received下的所有场景文件夹
    scene_folders = sorted([d for d in os.listdir(RECEIVED_ROOT) 
                           if os.path.isdir(os.path.join(RECEIVED_ROOT, d))])
    
    for scene_name in scene_folders:
        scene_received_path = os.path.join(RECEIVED_ROOT, scene_name)
        scene_unpack_path = os.path.join(UNPACK_RAW_ROOT, scene_name)
        
        # 创建目标场景目录
        os.makedirs(scene_unpack_path, exist_ok=True)
        
        # 查找 .RAWMIPI10 文件
        # rawmipi_files = sorted(glob.glob(os.path.join(scene_received_path, '*.RAWMIPI10')))
        rawmipi_files = sorted(glob.glob(os.path.join(scene_received_path, '*.raw')))
        
        if not rawmipi_files:
            print(f"[跳过] 场景 '{scene_name}' 下未找到 .RAWMIPI10 文件")
            continue
        
        print(f"\n[场景] {scene_name} ({len(rawmipi_files)} 个RAWMIPI10文件)")
        
        for rawmipi_file in rawmipi_files:
            rawmipi_basename = os.path.basename(rawmipi_file)
            # 将后缀从 .RAWMIPI10 改为 .raw
            output_basename = os.path.splitext(rawmipi_basename)[0] + '.raw'
            out_filepath = os.path.join(scene_unpack_path, output_basename)
            
            print(f"  -> 处理: {rawmipi_basename} -> {output_basename}", end=' ... ')
            
            try:
                rawPreprocess(
                    PARAMS['height'], PARAMS['width'], PARAMS['stride'],
                    PARAMS['in_bit'], PARAMS['out_bit'],
                    rawmipi_file, out_filepath
                )
                print("✅ 完成")
            except Exception as e:
                print(f"❌ 失败 ({e})")

if __name__ == '__main__':
    print(f"运行环境: {sys.platform} | Python: {sys.version}")
    process_all_scenes()
    print(f"\n🎉 所有场景处理完毕！")