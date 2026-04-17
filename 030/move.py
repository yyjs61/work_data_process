import os
import numpy as np

ROOT = "/data/030_Test_0327_for16-9_20260327/"

SRC_ROOT = os.path.join(ROOT, "received")
DST_ROOT = os.path.join(ROOT, "unpack_raw")

# 候选右移位数（常见：14bit -> 16bit padding）
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

for scene in sorted(os.listdir(SRC_ROOT)):
    src_scene_dir = os.path.join(SRC_ROOT, scene)

    dst_scene_dir = os.path.join(DST_ROOT, scene)
    os.makedirs(dst_scene_dir, exist_ok=True)

    for fname in sorted(os.listdir(src_scene_dir)):
        if not fname.endswith('.raw'):
            continue
        src_file = os.path.join(src_scene_dir, fname)

        # 读取 raw（RawPlain16LSB14bit 一般是 uint16）
        data = np.fromfile(src_file, dtype=np.uint16)

        shift_bits = detect_shift_bits(data)
        if shift_bits > 0:
            print(f"[SHIFT] {scene}/{fname}  >> {shift_bits}")
            data = data >> shift_bits
        else:
            print(f"[KEEP ] {scene}/{fname}")

        # dst_fname = fname + ".raw"
        dst_fname = fname
        dst_file = os.path.join(dst_scene_dir, dst_fname)

        data.tofile(dst_file)

    print(f"[OK] scene done: {scene}")
