import os
import re


def rename_folders_with_space(target_dir, merge_spaces=True):
    """
    将指定目录下所有文件夹名称中的空格替换为下划线
    
    Args:
        target_dir: 目标目录路径
        merge_spaces: 是否将多个连续空格合并为一个下划线
                     True  -> 多个空格用一个下划线代替 (推荐)
                     False -> 每个空格都用一个下划线代替
    """
    if not os.path.exists(target_dir):
        print(f"错误：目录 '{target_dir}' 不存在！")
        return
    
    folders = [f for f in os.listdir(target_dir) 
               if os.path.isdir(os.path.join(target_dir, f))]
    
    if not folders:
        print("该目录下没有找到文件夹。")
        return
    
    print(f"找到 {len(folders)} 个文件夹，准备重命名...")
    print(f"模式：{'多个空格合并为一个下划线' if merge_spaces else '每个空格替换为一个下划线'}\n")
    
    renamed_count = 0
    skipped_count = 0
    error_count = 0
    
    for folder_name in folders:
        old_path = os.path.join(target_dir, folder_name)
        
        # 检查名称中是否包含空格
        if ' ' in folder_name:
            # 根据模式选择替换方式
            if merge_spaces:
                # 多个连续空格替换为一个下划线
                new_name = re.sub(r'\s+', '_', folder_name)
            else:
                # 每个空格都替换为一个下划线
                new_name = folder_name.replace(' ', '_')
            
            new_path = os.path.join(target_dir, new_name)
            
            # 如果名称没有变化，跳过
            if new_name == folder_name:
                skipped_count += 1
                continue
            
            try:
                if os.path.exists(new_path):
                    print(f"跳过：'{folder_name}' -> 目标名称 '{new_name}' 已存在")
                    skipped_count += 1
                    continue
                
                os.rename(old_path, new_path)
                print(f"重命名：'{folder_name}' -> '{new_name}'")
                renamed_count += 1
                
            except Exception as e:
                print(f"错误：无法重命名 '{folder_name}' - {str(e)}")
                error_count += 1
        else:
            skipped_count += 1
    
    print(f"\n{'='*60}")
    print(f"重命名完成！")
    print(f"  成功重命名：{renamed_count} 个文件夹")
    print(f"  跳过：{skipped_count} 个文件夹")
    print(f"  错误：{error_count} 个文件夹")
    print(f"{'='*60}")


def preview_rename(target_dir, merge_spaces=True):
    """
    预览重命名效果，不实际执行
    
    Args:
        target_dir: 目标目录路径
        merge_spaces: 是否将多个连续空格合并为一个下划线
    """
    if not os.path.exists(target_dir):
        print(f"错误：目录 '{target_dir}' 不存在！")
        return
    
    folders = [f for f in os.listdir(target_dir) 
               if os.path.isdir(os.path.join(target_dir, f))]
    
    mode_desc = "多个空格合并为一个下划线" if merge_spaces else "每个空格替换为一个下划线"
    print(f"目录：{target_dir}")
    print(f"模式：{mode_desc}")
    print(f"{'='*80}")
    print(f"{'原名称':<40} {'->':<5} {'新名称':<40}")
    print(f"{'='*80}")
    
    will_rename = 0
    for folder_name in folders:
        if ' ' in folder_name:
            if merge_spaces:
                new_name = re.sub(r'\s+', '_', folder_name)
            else:
                new_name = folder_name.replace(' ', '_')
            
            if new_name != folder_name:
                print(f"{folder_name:<40} {'->':<5} {new_name:<40}")
                will_rename += 1
    
    if will_rename == 0:
        print("没有需要重命名的文件夹（名称中不含空格）")
    else:
        print(f"{'='*80}")
        print(f"共有 {will_rename} 个文件夹将被重命名")


def main():
    """主函数"""
    target_directory = r"D:\Data\2026_06\11\HY_IMX06A_20260601\black_level"
    
    print("="*80)
    print("文件夹批量重命名工具")
    print("功能：将文件夹名称中的空格替换为下划线")
    print("="*80)
    
    # 选择替换模式
    print("\n请选择替换模式：")
    print("  [1] 多个空格用一个下划线代替 (推荐，如 'A gain 1' -> 'A_gain_1')")
    print("  [2] 每个空格都用一个下划线代替 (如 'A  gain  1' -> 'A__gain__1')")
    
    choice = input("\n请输入选项 (1/2，默认1): ").strip()
    
    if choice == '2':
        merge_spaces = False
    else:
        merge_spaces = True
    
    # 预览
    print("\n" + "="*80)
    print("【预览模式】")
    preview_rename(target_directory, merge_spaces)
    
    # 确认执行
    print("\n" + "="*80)
    confirm = input("是否执行重命名操作？(y/n): ").strip().lower()
    
    if confirm in ('y', 'yes'):
        print("\n【执行重命名】")
        rename_folders_with_space(target_directory, merge_spaces)
    else:
        print("\n已取消操作。")


if __name__ == "__main__":
    main()