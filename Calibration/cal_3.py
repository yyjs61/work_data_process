import os
import numpy as np

ROOT = "/data/MCC_0212"
SRC_ROOT = os.path.join(ROOT, "origin")
BLACK_LEVEL_ROOT = os.path.join(ROOT, "NoiseProfile")

# 每个 scene 对应的原始位宽和低位 padding
SCENE_CONFIG = {
    "1X": {"bit_depth": 14, "padding": 2, "bayer": "BGGR"},
    "2X": {"bit_depth": 10, "padding": 4, "bayer": "BGGR"},
}

for scene, config in SCENE_CONFIG.items():
    src_scene_root = os.path.join(SRC_ROOT, "NoiseProfile", scene)
    if not os.path.isdir(src_scene_root):
        print(f"[SKIP] no dir: {src_scene_root}")
        continue

    for root_dir, dirs, files in os.walk(src_scene_root):
        relative_path = os.path.relpath(root_dir, os.path.join(SRC_ROOT, "NoiseProfile"))
        dst_scene_dir = os.path.join(BLACK_LEVEL_ROOT, relative_path)
        os.makedirs(dst_scene_dir, exist_ok=True)

        for fname in sorted(files):
            # 只处理 .raw 文件
            if not fname.lower().endswith(".raw"):
                continue

            src_file = os.path.join(root_dir, fname)
            data = np.fromfile(src_file, dtype=np.uint16)

            # 根据配置去除低位 padding
            shift_bits = config["padding"]
            if shift_bits > 0:
                data = data >> shift_bits
                print(f"[SHIFT] {relative_path}/{fname}: >> {shift_bits}")

            dst_file = os.path.join(dst_scene_dir, fname)
            data.tofile(dst_file)

        if any(f.lower().endswith(".raw") for f in files):
            print(f"[OK] {relative_path}")
