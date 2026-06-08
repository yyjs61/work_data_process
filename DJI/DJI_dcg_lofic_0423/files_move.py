#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISP测试素材整理脚本
功能：
1. 将iphone17pro下的图片和视频移动到benchmark_videos目录，并重命名为场景名
2. 将braw_lofic_dump文件夹下的内容移动到rawdump目录下
"""

import os
import shutil
import glob
from pathlib import Path


def organize_media_files(base_path):
    """
    整理媒体文件（JPG和MOV）
    
    Args:
        base_path: 基础路径，包含received和20260513_material目录
    """
    received_path = os.path.join(base_path, 'received')
    benchmark_path = os.path.join(base_path, '20260513_material', 'benchmark_videos')
    
    # 创建benchmark_videos目录（如果不存在）
    os.makedirs(benchmark_path, exist_ok=True)
    
    # 遍历所有场景文件夹
    if not os.path.exists(received_path):
        print(f"错误：找不到received目录：{received_path}")
        return
    
    scene_folders = [f for f in os.listdir(received_path) 
                     if os.path.isdir(os.path.join(received_path, f))]
    
    for scene_name in scene_folders:
        scene_path = os.path.join(received_path, scene_name)
        iphone_path = os.path.join(scene_path, 'iphone17pro')
        
        if not os.path.exists(iphone_path):
            print(f"跳过：找不到iphone17pro目录 - {iphone_path}")
            continue
        
        # 查找JPG和MOV文件
        files_to_move = []
        for file in os.listdir(iphone_path):
            if file.lower().endswith(('.jpg', '.jpeg', '.mov')):
                files_to_move.append(file)
        
        # 移动并重命名文件
        for file in files_to_move:
            src_path = os.path.join(iphone_path, file)
            
            # 获取文件扩展名
            _, ext = os.path.splitext(file)
            ext = ext.lower()
            
            # 生成新文件名（使用场景名）
            new_filename = f"{scene_name}{ext}"
            dst_path = os.path.join(benchmark_path, new_filename)
            
            try:
                shutil.move(src_path, dst_path)
                print(f"移动：{src_path} -> {dst_path}")
            except Exception as e:
                print(f"错误：移动文件失败 {src_path} -> {dst_path}: {e}")


def organize_rawdump_files(base_path):
    """
    整理rawdump目录下的braw_lofic_dump文件夹内容
    
    Args:
        base_path: 基础路径，包含received目录
    """
    received_path = os.path.join(base_path, 'received')
    
    if not os.path.exists(received_path):
        print(f"错误：找不到received目录：{received_path}")
        return
    
    scene_folders = [f for f in os.listdir(received_path) 
                     if os.path.isdir(os.path.join(received_path, f))]
    
    for scene_name in scene_folders:
        scene_path = os.path.join(received_path, scene_name)
        rawdump_path = os.path.join(scene_path, 'rawdump')
        
        if not os.path.exists(rawdump_path):
            print(f"跳过：找不到rawdump目录 - {rawdump_path}")
            continue
        
        # 查找braw_lofic_dump*文件夹
        braw_folders = glob.glob(os.path.join(rawdump_path, 'braw_lofic_dump*'))
        
        for braw_folder in braw_folders:
            if not os.path.isdir(braw_folder):
                continue
            
            print(f"\n处理：{braw_folder}")
            
            # 移动文件夹下的所有内容到rawdump目录
            for item in os.listdir(braw_folder):
                src_path = os.path.join(braw_folder, item)
                dst_path = os.path.join(rawdump_path, item)
                
                try:
                    if os.path.isdir(src_path):
                        shutil.move(src_path, dst_path)
                        print(f"  移动目录：{item}")
                    else:
                        shutil.move(src_path, dst_path)
                        print(f"  移动文件：{item}")
                except Exception as e:
                    print(f"  错误：移动失败 {item}: {e}")
            
            # 删除空的braw_lofic_dump文件夹
            try:
                if not os.listdir(braw_folder):
                    os.rmdir(braw_folder)
                    print(f"  删除空目录：{braw_folder}")
            except Exception as e:
                print(f"  警告：删除目录失败 {braw_folder}: {e}")


def main():
    # 基础路径（根据实际情况修改）
    base_path = r'D:\Data\DJI_OV50X\20260513\0511_ov50x_raw素材-2026-05-13\20260513_material'
    
    print("=" * 80)
    print("开始整理媒体文件...")
    print("=" * 80)
    organize_media_files(base_path)
    
    print("\n" + "=" * 80)
    print("开始整理rawdump文件...")
    print("=" * 80)
    organize_rawdump_files(base_path)
    
    print("\n" + "=" * 80)
    print("整理完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()