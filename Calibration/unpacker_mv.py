#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISP Raw数据批量解包预处理脚本
功能：遍历origin下的NoiseProfile/BlackLevel场景，将.raw文件解包并输出到同级目标目录
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
    lib.sequentialUnpacker(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth, in_filepath_c_str, out_filepath_c_str)


def process_all_scenes():
    # ================= 配置区 =================
    # BASE_ROOT = '/home/user/afs_data/202605/18/Cal/iac4_dcg_er4'
    # BASE_ROOT = r'D:\etc\IAC4\data\data_IAC4\iac4_dcg_er16'
    BASE_ROOT = r'D:\etc\IAC4\data\data_IAC4'
    ORIGIN_ROOT = os.path.join(BASE_ROOT, 'origin')
    CATEGORIES = ['NoiseProfile', 'BlackLevel', 'BlackLevel_EVT_2p5_exparatio4']
    
    # 解包参数 (可根据实际Sensor规格或从meta/txt中动态解析修改)
    PARAMS = {
        'height': 3600,
        'width': 4096,
        'stride': 6144,
        'in_bit': 12,
        'out_bit': 12
    }
    # ==========================================

    if not os.path.exists(ORIGIN_ROOT):
        print(f"[错误] 源目录不存在: {ORIGIN_ROOT}")
        sys.exit(1)

    for category in CATEGORIES:
        origin_cat_path = os.path.join(ORIGIN_ROOT, category)
        target_cat_path = os.path.join(BASE_ROOT, category)

        if not os.path.exists(origin_cat_path):
            print(f"[警告] 跳过不存在的类别目录: {origin_cat_path}")
            continue

        # 确保目标类别目录存在
        os.makedirs(target_cat_path, exist_ok=True)
        print(f"\n{'='*60}")
        print(f"开始处理类别: {category}")
        print(f"{'='*60}")

        # 遍历所有场景文件夹
        scene_folders = sorted([d for d in os.listdir(origin_cat_path) 
                                if os.path.isdir(os.path.join(origin_cat_path, d))])
        
        for scene_name in scene_folders:
            scene_origin_path = os.path.join(origin_cat_path, scene_name)
            scene_target_path = os.path.join(target_cat_path, scene_name)
            
            # 创建目标场景目录
            os.makedirs(scene_target_path, exist_ok=True)

            # 仅查找 .raw 文件，自动忽略 .meta, .txt 及其他文件
            raw_files = sorted(glob.glob(os.path.join(scene_origin_path, '*.raw')))
            if not raw_files:
                print(f"[跳过] 场景 '{scene_name}' 下未找到 .raw 文件")
                continue

            print(f"\n[场景] {scene_name} ({len(raw_files)} 个raw文件)")
            for raw_file in raw_files:
                raw_basename = os.path.basename(raw_file)
                out_filepath = os.path.join(scene_target_path, raw_basename)

                print(f"  -> 处理: {raw_basename}", end=' ... ')
                try:
                    rawPreprocess(
                        PARAMS['height'], PARAMS['width'], PARAMS['stride'],
                        PARAMS['in_bit'], PARAMS['out_bit'],
                        raw_file, out_filepath
                    )
                    print("✅ 完成")
                except Exception as e:
                    print(f"❌ 失败 ({e})")


if __name__ == '__main__':
    print(f"运行环境: {sys.platform} | Python: {sys.version}")
    process_all_scenes()
    print("\n🎉 所有场景处理完毕！")