#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解包后文件整理脚本
功能：将rec_decode.bin移动到上级目录并重命名为.raw文件
"""
import os
import glob
import shutil
from pathlib import Path

def clean_filename(folder_name):
    """
    清理文件夹名，生成raw文件名
    # 例如：req[1]_frame[3]_..._000884_L -> req[1]_frame[3]_..._000884.raw
    """
    # 去掉末尾的 _L 或 _R 等标记
    base_name = folder_name
    # if base_name.endswith('_L'):
    #     base_name = base_name[:-2]
    # elif base_name.endswith('_R'):
    #     base_name = base_name[:-2]
    
    # 添加.raw后缀
    return base_name + '.raw'

def process_unpack_raw():
    # ================= 配置区 =================
    BASE_ROOT = r"D:\Data\2026_05\22\blc_raw"
    UNPACK_RAW_ROOT = os.path.join(BASE_ROOT, 'unpack_raw')
    
    # ==========================================
    
    if not os.path.exists(UNPACK_RAW_ROOT):
        print(f"[错误] 目录不存在: {UNPACK_RAW_ROOT}")
        return
    
    print(f"{'='*70}")
    print(f"解包后文件整理工具")
    print(f"{'='*70}")
    print(f"处理目录: {UNPACK_RAW_ROOT}")
    print(f"{'='*70}\n")
    
    # 遍历unpack_raw下的所有场景文件夹
    scene_folders = sorted([d for d in os.listdir(UNPACK_RAW_ROOT) 
                           if os.path.isdir(os.path.join(UNPACK_RAW_ROOT, d))])
    
    if not scene_folders:
        print(f"[警告] 未找到任何场景文件夹")
        return
    
    total_files = 0
    success_count = 0
    
    for scene_idx, scene_name in enumerate(scene_folders, 1):
        scene_path = os.path.join(UNPACK_RAW_ROOT, scene_name)
        
        print(f"\n[{scene_idx}/{len(scene_folders)}] 场景: {scene_name}")
        
        # 查找场景下所有包含rec_decode.bin的子文件夹
        sub_folders = [d for d in os.listdir(scene_path) 
                      if os.path.isdir(os.path.join(scene_path, d))]
        
        if not sub_folders:
            print(f"  [跳过] 未找到子文件夹")
            continue
        
        processed_count = 0
        for folder_name in sorted(sub_folders):
            folder_path = os.path.join(scene_path, folder_name)
            rec_decode_file = os.path.join(folder_path, 'rec_decode.bin')
            
            # 检查rec_decode.bin是否存在
            if not os.path.exists(rec_decode_file):
                continue
            
            # 生成目标文件名
            target_filename = clean_filename(folder_name)
            target_path = os.path.join(scene_path, target_filename)
            
            print(f"  → {folder_name}")
            print(f"    -> {target_filename}")
            
            try:
                # 移动并重命名文件
                shutil.move(rec_decode_file, target_path)
                
                # 删除空文件夹
                try:
                    os.rmdir(folder_path)
                    print(f"    ✓ 已删除空文件夹")
                except OSError:
                    # 文件夹非空，保留
                    print(f"    ⊘ 文件夹非空，保留")
                
                success_count += 1
                processed_count += 1
                
            except Exception as e:
                print(f"    ✗ 失败: {e}")
        
        if processed_count == 0:
            print(f"  [跳过] 未找到rec_decode.bin文件")
        
        total_files += processed_count
    
    # 统计结果
    print(f"\n{'='*70}")
    print(f"处理完成！")
    print(f"  总文件数: {total_files}")
    print(f"  成功: {success_count}")
    print(f"{'='*70}")

if __name__ == '__main__':
    import sys
    print(f"Python版本: {sys.version}")
    print(f"平台: {sys.platform}\n")
    
    try:
        process_unpack_raw()
    except KeyboardInterrupt:
        print("\n\n[用户中断] 程序已终止")
    except Exception as e:
        print(f"\n[致命错误] {e}")
        import traceback
        traceback.print_exc()