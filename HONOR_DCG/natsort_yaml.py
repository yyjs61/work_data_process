import os
import glob
import re

ROOT = '/data/HP3_QuadBayer_20251217_ISO12233_TE42'
RECEIVED_DIR = os.path.join(ROOT, 'received')

def get_req_val(filename):
    """从文件名中提取 req 数值"""
    m = re.search(r'_req\[(\d+)\]', filename)
    return int(m.group(1)) if m else -1

def add_prefix_to_scene(scene_dir):
    raw_files = glob.glob(os.path.join(scene_dir, '*.raw*'))
    if not raw_files:
        return

    for old_path in raw_files:
        base = os.path.basename(old_path)
        req_val = get_req_val(base)
        if req_val == -1:
            continue
        prefix = f"{req_val:03d}_"

        if not base.startswith(prefix):
            new_name = prefix + base
            new_path = os.path.join(scene_dir, new_name)
            os.rename(old_path, new_path)
            print(f"重命名: {base} -> {new_name}")

def main():
    scenes = sorted(os.listdir(RECEIVED_DIR))
    for scene in scenes:
        scene_path = os.path.join(RECEIVED_DIR, scene)
        if os.path.isdir(scene_path):
            print(f"\n处理场景: {scene}")
            add_prefix_to_scene(scene_path)

if __name__ == "__main__":
    main()
