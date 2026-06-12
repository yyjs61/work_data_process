import os
import sys

def process_scene_folder(scene_dir, do_prefix=True, do_suffix=True):
    """处理单个场景文件夹，执行重命名规则"""
    if not os.path.isdir(scene_dir):
        return 0, 0, 0, 0

    success, skipped, conflicts, errors = 0, 0, 0, 0

    try:
        files = os.listdir(scene_dir)
    except PermissionError:
        print(f"  ❌ 权限不足，跳过: {scene_dir}")
        return 0, 0, 0, 0

    for filename in files:
        old_path = os.path.join(scene_dir, filename)
        if not os.path.isfile(old_path):
            continue

        new_filename = filename
        changed = False

        # 规则1：提取第一个下划线前的内容作为新文件名
        if do_prefix:
            name, ext = os.path.splitext(filename)
            if '_' in name:
                new_filename = f"{name.split('_')[0]}{ext}"
                changed = True
            else:
                # 原逻辑：无下划线则跳过该文件
                skipped += 1
                continue

        # 规则2：将 .dat 后缀改为 .raw
        if do_suffix and new_filename.lower().endswith('.dat'):
            new_filename = new_filename[:-4] + '.raw'
            changed = True

        # 无需修改则跳过
        if not changed or filename == new_filename:
            skipped += 1
            continue

        new_path = os.path.join(scene_dir, new_filename)

        # 冲突检查
        if os.path.exists(new_path):
            print(f"  ⚠️ [冲突] {filename} -> {new_filename} (目标已存在)")
            conflicts += 1
            continue

        # 执行重命名
        try:
            os.rename(old_path, new_path)
            print(f"  ✅ [成功] {filename} -> {new_filename}")
            success += 1
        except Exception as e:
            print(f"  ❌ [失败] {filename} 出错: {e}")
            errors += 1

    return success, skipped, conflicts, errors


def main():
    # ================= 配置区 =================
    ROOT_DIR = r"D:\Data\2026_06\09"
    SUB_PATH = "vnt"  # 子路径名，如 "received"、"dat" 等
    
    # 控制是否启用两条规则（可按需改为 False）
    ENABLE_PREFIX_RENAME = True  # 提取 _ 前的内容
    # ENABLE_DAT_TO_RAW    = True  # .dat 转 .raw
    ENABLE_DAT_TO_RAW    = True  # .dat 转 .raw
    # ==========================================

    target_base = os.path.join(ROOT_DIR, SUB_PATH)
    if not os.path.exists(target_base):
        print(f"❌ 错误：目录不存在 -> {target_base}")
        return
    if not os.path.isdir(target_base):
        print(f"❌ 错误：路径不是目录 -> {target_base}")
        return

    print(f"📂 开始处理目录：{target_base}")
    print("=" * 60)

    # 获取所有一级子目录（即场景文件夹）
    try:
        scene_dirs = [
            os.path.join(target_base, d) 
            for d in os.listdir(target_base) 
            if os.path.isdir(os.path.join(target_base, d))
        ]
        scene_dirs.sort()  # 按名称排序，保证处理顺序一致
    except PermissionError:
        print("❌ 错误：没有权限访问该目录")
        return

    if not scene_dirs:
        print("📭 未找到任何场景文件夹，程序退出。")
        return

    print(f"🔍 共找到 {len(scene_dirs)} 个场景文件夹，开始逐个处理...\n")

    total_s, total_sk, total_c, total_e = 0, 0, 0, 0

    for i, scene_dir in enumerate(scene_dirs, 1):
        scene_name = os.path.basename(scene_dir)
        print(f"📁 [{i}/{len(scene_dirs)}] 处理场景: {scene_name}")
        
        s, sk, c, e = process_scene_folder(
            scene_dir, 
            do_prefix=ENABLE_PREFIX_RENAME, 
            do_suffix=ENABLE_DAT_TO_RAW
        )
        total_s += s
        total_sk += sk
        total_c += c
        total_e += e
        print("-" * 40)

    print("\n" + "=" * 60)
    print("🏁 全部处理完成！")
    print(f"📊 总计 -> ✅ 成功: {total_s} | ⏭️ 跳过: {total_sk} | ⚠️ 冲突: {total_c} | ❌ 失败: {total_e}")
    input("\n按回车键退出...")


if __name__ == "__main__":
    main()