#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本名称: getSceneYaml_2.py
功能说明: 为整理后的目录结构中的每个场景生成对应的YAML配置文件

工作流程:
1. 读取基础YAML配置文件(s0.yaml)
2. 遍历顶级目录下的unpack_raw文件夹中的所有场景
3. 为每个场景填充对应的S3路径信息，生成YAML配置文件
4. 生成的YAML文件保存到 SceneYamls/{dataset_name}/ 目录

适用目录结构:
./
├─unpack_raw/
│  ├─场景1/
│  ├─场景2/
│  └─...
├─yamls_eachFrame/
│  ├─场景1/
│  ├─场景2/
│  └─...
├─s0.yaml
└─...

"""

import os
import yaml

# ===================== 配置部分 =====================
# 定义S3根路径
ROOT_PATH = 's3://isp_projectdata/VideoSupernightData/VNT/IMX678_20260428'

# 定义OneDrive_1_4-28-2026的根目录
# PROJECT_ROOT = r'D:\Data\2026_04\28\OneDrive_1_4-28-2026'
PROJECT_ROOT = r'D:\Data\2026_05\18\Test_data_260515'

# 本地目录配置（绝对路径）
UNPACK_RAW_DIR = os.path.join(PROJECT_ROOT, 'unpack_raw')
YAMLS_EACHFRAME_DIR = os.path.join(PROJECT_ROOT, 'yamls_eachFrame')
BASE_YAML_FILE = os.path.join(PROJECT_ROOT, 's0.yaml')
OUTPUT_BASE_DIR = os.path.join(PROJECT_ROOT, 'SceneYamls')

# ===================== 主程序 =====================

def get_dataset_name(root_path):
    """
    从S3路径中提取数据集名称
    
    参数:
        root_path (str): S3根路径
    
    返回:
        str: 数据集名称
    """
    return root_path.strip('/').split('/')[-1]


def load_base_yaml(yaml_file):
    """
    加载基础YAML配置文件
    
    参数:
        yaml_file (str): YAML文件路径
    
    返回:
        dict: YAML配置内容，如果文件不存在则返回None
    """
    if not os.path.isfile(yaml_file):
        print(f"错误: 基础YAML文件不存在: {yaml_file}")
        return None
    
    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print(f"✓ 成功加载基础YAML文件: {yaml_file}\n")
        return config
    except Exception as e:
        print(f"错误: 读取YAML文件失败: {e}")
        return None


def generate_scene_yamls(root_path, unpack_raw_dir, output_dir, base_config):
    """
    为每个场景生成对应的YAML配置文件
    
    参数:
        root_path (str): S3根路径
        unpack_raw_dir (str): unpack_raw本地目录路径
        output_dir (str): 输出目录路径
        base_config (dict): 基础YAML配置内容
    """
    
    # 检查unpack_raw目录是否存在
    if not os.path.isdir(unpack_raw_dir):
        print(f"错误: unpack_raw目录不存在: {unpack_raw_dir}")
        return
    
    # 获取数据集名称
    dataset_name = get_dataset_name(root_path)
    
    # 创建输出目录
    scene_output_dir = os.path.join(output_dir, dataset_name)
    os.makedirs(scene_output_dir, exist_ok=True)
    
    print(f"S3根路径: {root_path}")
    print(f"数据集名称: {dataset_name}")
    print(f"输出目录: {scene_output_dir}\n")
    print("=" * 70)
    print("开始生成场景YAML配置文件\n")
    
    # 遍历unpack_raw目录下的所有场景
    scenes = os.listdir(unpack_raw_dir)
    
    if not scenes:
        print("⚠️  未找到任何场景")
        return
    
    print(f"找到 {len(scenes)} 个场景\n")
    
    for scene_name in sorted(scenes):
        scene_path = os.path.join(unpack_raw_dir, scene_name)
        
        # 只处理文件夹
        if not os.path.isdir(scene_path):
            continue
        
        # 复制基础配置
        scene_config = dict(base_config)
        
        # 设置S3路径，使用 '/' 连接保证YAML中不出现Windows反斜杠
        scene_config['dir_name'] = f"{root_path.rstrip('/')}/unpack_raw/{scene_name}"
        scene_config['eachframe_yaml_path'] = f"{root_path.rstrip('/')}/yamls_eachFrame/{scene_name}"
        
        # 生成输出文件路径
        output_yaml_file = os.path.join(scene_output_dir, f'{scene_name}.yaml')
        
        # 写入YAML文件
        try:
            with open(output_yaml_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(scene_config, f, allow_unicode=True)
            print(f"✓ {scene_name}")
            print(f"  → dir_name: {scene_config['dir_name']}")
            print(f"  → eachframe_yaml_path: {scene_config['eachframe_yaml_path']}\n")
        except Exception as e:
            print(f"✗ 写入失败: {scene_name} - {e}\n")
    
    print("=" * 70)
    print(f"所有场景YAML配置文件生成完成！")
    print(f"输出目录: {scene_output_dir}")


if __name__ == '__main__':
    """
    主函数入口
    """
    
    # 加载基础YAML配置文件
    base_config = load_base_yaml(BASE_YAML_FILE)
    
    if base_config is None:
        print("错误: 无法加载基础YAML文件，脚本退出")
    else:
        # 生成场景YAML文件
        generate_scene_yamls(ROOT_PATH, UNPACK_RAW_DIR, OUTPUT_BASE_DIR, base_config)
