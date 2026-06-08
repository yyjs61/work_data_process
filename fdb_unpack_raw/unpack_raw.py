#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAW文件批量解包脚本
功能：遍历received下的场景文件夹，将指定大小的RAW文件解包到unpack_raw目录
"""
import os
import glob
import yaml
import subprocess
import shutil
from pathlib import Path

def update_cfg_yaml(cfg_path, input_file, output_dir):
    """更新cfg.yaml文件中的input_stm_path和dump_dir"""
    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    
    # 更新输入文件路径和输出目录
    cfg['input_stm_path'] = input_file
    cfg['dump_dir'] = output_dir
    
    # 保存更新后的cfg.yaml
    with open(cfg_path, 'w', encoding='utf-8') as f:
        yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True)
    
    print(f"  ✓ 已更新cfg.yaml")
    print(f"    输入: {input_file}")
    print(f"    输出: {output_dir}")

def run_unpacker(exe_path, cfg_path):
    """执行解包程序"""
    cmd = f'"{exe_path}" "{cfg_path}"'
    print(f"  → 执行命令: {cmd}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            print(f"  ✓ 解包成功")
            if result.stdout:
                print(f"    输出: {result.stdout.strip()[:200]}")
            return True
        else:
            print(f"  ✗ 解包失败 (返回码: {result.returncode})")
            if result.stderr:
                print(f"    错误: {result.stderr.strip()[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ 执行异常: {e}")
        return False

def process_all_scenes():
    # ================= 配置区 =================
    BASE_ROOT = r"D:\Data\2026_05\22\blc_raw"
    RECEIVED_ROOT = os.path.join(BASE_ROOT, 'received')
    UNPACK_RAW_ROOT = os.path.join(BASE_ROOT, 'unpack_raw')
    
    # FDB解包工具路径
    FDB_ROOT = r"D:\Work\Code\00_data_process\data_process_use\fdb_unpack_raw"
    CFG_YAML_PATH = os.path.join(FDB_ROOT, '64x4', 'cfg.yaml')
    EXE_PATH = os.path.join(FDB_ROOT, 'win', 'fbd_INTERNAL_USE.exe')
    
    # 目标文件大小 (22,020,096 字节)
    TARGET_FILE_SIZE = 22020096
    
    # ==========================================
    
    # 验证路径
    if not os.path.exists(RECEIVED_ROOT):
        print(f"[错误] 源目录不存在: {RECEIVED_ROOT}")
        return
    
    if not os.path.exists(CFG_YAML_PATH):
        print(f"[错误] cfg.yaml不存在: {CFG_YAML_PATH}")
        return
    
    if not os.path.exists(EXE_PATH):
        print(f"[错误] 解包程序不存在: {EXE_PATH}")
        return
    
    print(f"{'='*70}")
    print(f"RAW文件批量解包工具")
    print(f"{'='*70}")
    print(f"源目录: {RECEIVED_ROOT}")
    print(f"目标目录: {UNPACK_RAW_ROOT}")
    print(f"目标文件大小: {TARGET_FILE_SIZE:,} 字节")
    print(f"{'='*70}\n")
    
    # 遍历received下的所有场景文件夹
    scene_folders = sorted([d for d in os.listdir(RECEIVED_ROOT) 
                           if os.path.isdir(os.path.join(RECEIVED_ROOT, d))])
    
    if not scene_folders:
        print(f"[警告] 未找到任何场景文件夹")
        return
    
    total_files = 0
    success_count = 0
    
    for scene_idx, scene_name in enumerate(scene_folders, 1):
        scene_received_path = os.path.join(RECEIVED_ROOT, scene_name)
        scene_unpack_path = os.path.join(UNPACK_RAW_ROOT, scene_name)
        
        # 创建目标场景目录
        os.makedirs(scene_unpack_path, exist_ok=True)
        
        print(f"\n[{scene_idx}/{len(scene_folders)}] 场景: {scene_name}")
        print(f"  源路径: {scene_received_path}")
        
        # 查找所有RAW文件
        raw_files = glob.glob(os.path.join(scene_received_path, '*.raw'))
        
        # 筛选目标大小的文件
        target_files = []
        for raw_file in raw_files:
            file_size = os.path.getsize(raw_file)
            if file_size == TARGET_FILE_SIZE:
                target_files.append(raw_file)
            else:
                print(f"  ⊘ 跳过 {os.path.basename(raw_file)} (大小: {file_size:,} 字节)")
        
        if not target_files:
            print(f"  [跳过] 未找到大小为 {TARGET_FILE_SIZE:,} 字节的RAW文件")
            continue
        
        print(f"  找到 {len(target_files)} 个目标文件")
        
        # 处理每个目标文件
        for raw_file in sorted(target_files):
            total_files += 1
            raw_basename = os.path.basename(raw_file)
            raw_name_without_ext = os.path.splitext(raw_basename)[0]
            
            print(f"\n  [{total_files}] 处理: {raw_basename}")
            print(f"      大小: {os.path.getsize(raw_file):,} 字节")
            
            # 创建该文件的输出子目录
            file_output_dir = os.path.join(scene_unpack_path, raw_name_without_ext)
            os.makedirs(file_output_dir, exist_ok=True)
            
            # 备份原始cfg.yaml
            cfg_backup_path = CFG_YAML_PATH + '.backup'
            if not os.path.exists(cfg_backup_path):
                shutil.copy2(CFG_YAML_PATH, cfg_backup_path)
            
            try:
                # 更新cfg.yaml
                update_cfg_yaml(CFG_YAML_PATH, raw_file, file_output_dir)
                
                # 执行解包
                if run_unpacker(EXE_PATH, CFG_YAML_PATH):
                    success_count += 1
                    
                    # 检查输出文件
                    output_files = glob.glob(os.path.join(file_output_dir, '*'))
                    if output_files:
                        print(f"  ✓ 生成 {len(output_files)} 个输出文件:")
                        for out_file in output_files[:5]:  # 只显示前5个
                            size = os.path.getsize(out_file)
                            print(f"    - {os.path.basename(out_file)} ({size:,} 字节)")
                        if len(output_files) > 5:
                            print(f"    ... 还有 {len(output_files) - 5} 个文件")
                else:
                    print(f"  ✗ 解包失败")
            
            finally:
                # 恢复原始cfg.yaml
                if os.path.exists(cfg_backup_path):
                    shutil.copy2(cfg_backup_path, CFG_YAML_PATH)
    
    # 统计结果
    print(f"\n{'='*70}")
    print(f"处理完成！")
    print(f"  总文件数: {total_files}")
    print(f"  成功: {success_count}")
    print(f"  失败: {total_files - success_count}")
    print(f"{'='*70}")

if __name__ == '__main__':
    import sys
    print(f"Python版本: {sys.version}")
    print(f"平台: {sys.platform}\n")
    
    try:
        process_all_scenes()
    except KeyboardInterrupt:
        print("\n\n[用户中断] 程序已终止")
    except Exception as e:
        print(f"\n[致命错误] {e}")
        import traceback
        traceback.print_exc()