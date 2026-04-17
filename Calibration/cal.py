import os
import numpy as np

# ROOT = "/data/030_CALI_0326"
ROOT = "/home/user/afs_data/LeeSin_Xie/data/RatingData"

SRC_ROOT = os.path.join(ROOT, "origin")
NOISE_PROFILE_ROOT = os.path.join(ROOT, "NoiseProfile")
BLACK_LEVEL_ROOT = os.path.join(ROOT, "BlackLevel")

MAP = {
    "mcc_chart": NOISE_PROFILE_ROOT,
    "black_level": BLACK_LEVEL_ROOT,
}

SHIFT_CANDIDATES = [6, 4, 2]


def detect_shift_bits(arr, zero_ratio_thresh=0.999):
    for shift in [6, 4, 2]:
        mask = (1 << shift) - 1
        zeros = np.count_nonzero((arr & mask) == 0)
        ratio = zeros / arr.size
        if ratio > zero_ratio_thresh:
            return shift
    return 0

for src_type, dst_root in MAP.items():

    src_type_dir = os.path.join(SRC_ROOT, src_type)

    if not os.path.isdir(src_type_dir):
        print(f"[SKIP] Not found: {src_type_dir}")
        continue

    for root, _, files in os.walk(src_type_dir):

        for fname in sorted(files):

            if not fname.lower().endswith(("raw", "rawplain16lsb14bit")):
                continue

            src_file = os.path.join(root, fname)

            data = np.fromfile(src_file, dtype=np.uint16)

            shift_bits = detect_shift_bits(data)
            if shift_bits > 0:
                print(f"[SHIFT] {src_type}: {fname} >> {shift_bits}")
                data = data >> shift_bits

            # 保持相对路径结构
            rel_path = os.path.relpath(root, src_type_dir)
            dst_scene_dir = os.path.join(dst_root, rel_path)

            os.makedirs(dst_scene_dir, exist_ok=True)

            # dst_file = os.path.join(dst_scene_dir, fname + ".raw")
            dst_file = os.path.join(dst_scene_dir, fname)
            data.tofile(dst_file)

        print(f"[OK] Scanned: {root}")
