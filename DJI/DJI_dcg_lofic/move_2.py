import os
import numpy as np

# ROOT = "/home/user/afs_data/wang/0330_hnr_tele_hp3_quad_artifactTestData/"
# ROOT = "/home/user/afs_data/LeeSin_Xie/quadraw_for_yw_20260408/"
ROOT = r"D:\Data\DJI_OV50X\20260420\20260417_dcg_lofic/"

# SRC_ROOT = os.path.join(ROOT, "received")
# DST_ROOT = os.path.join(ROOT, "unpack_raw")

# 仅移位
SRC_ROOT = os.path.join(ROOT, "unpack_raw")
DST_ROOT = os.path.join(ROOT, "unpack_raw")

SHIFT_CANDIDATES = [6, 4, 2]


def detect_shift_bits(arr, zero_ratio_thresh=0.999):

    for shift in SHIFT_CANDIDATES:
        mask = (1 << shift) - 1
        zeros = np.count_nonzero((arr & mask) == 0)
        ratio = zeros / arr.size
        if ratio > zero_ratio_thresh:
            return shift
    return 0


os.makedirs(DST_ROOT, exist_ok=True)

# 遍历 received 下的所有项
for scene in sorted(os.listdir(SRC_ROOT)):
    src_scene_path = os.path.join(SRC_ROOT, scene)
    
    # 跳过 json 文件，只处理文件夹
    if not os.path.isdir(src_scene_path):
        print(f"[SKIP] {scene} (not a directory)")
        continue
    
    dst_scene_dir = os.path.join(DST_ROOT, scene)
    os.makedirs(dst_scene_dir, exist_ok=True)
    
    # 处理场景文件夹下的 raw 文件
    for fname in sorted(os.listdir(src_scene_path)):
        if not fname.endswith('.raw'):
        # if not fname.endswith('.dng'):
            # 跳过其他非 raw 文件
            continue
        
        src_file = os.path.join(src_scene_path, fname)
        
        # 确保是文件而不是目录
        if not os.path.isfile(src_file):
            continue

        data = np.fromfile(src_file, dtype=np.uint16)

        shift_bits = detect_shift_bits(data)
        # shift_bits = 4
        if shift_bits > 0:
            print(f"[SHIFT] {scene}/{fname}  >> {shift_bits}")
            data = data >> shift_bits
        else:
            print(f"[KEEP ] {scene}/{fname}")

        dst_fname = fname.split(".")[0] + ".raw"
        dst_file = os.path.join(dst_scene_dir, dst_fname)

        data.tofile(dst_file)

    print(f"[OK] scene done: {scene}")