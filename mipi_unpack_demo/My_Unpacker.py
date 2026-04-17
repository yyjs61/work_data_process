import numpy as np
import os
import glob


def unpack_rawmipi14(file_path, width, height, stride):
    raw_data = np.fromfile(file_path, dtype=np.uint8)
    unpacked_data = np.zeros((height, width), dtype=np.uint16)

    for row in range(height):
        row_start = row * stride
        row_bytes = raw_data[row_start: row_start + stride]

        groups = row_bytes.reshape(-1, 7)

        b0 = groups[:, 0].astype(np.uint16)
        b1 = groups[:, 1].astype(np.uint16)
        b2 = groups[:, 2].astype(np.uint16)
        b3 = groups[:, 3].astype(np.uint16)
        b4 = groups[:, 4].astype(np.uint16)
        b5 = groups[:, 5].astype(np.uint16)
        b6 = groups[:, 6].astype(np.uint16)

        unpacked_data[row, 0::4] = (b0 << 6) | (b4 & 0x3F)
        unpacked_data[row, 1::4] = (b1 << 6) | ((b4 >> 6) | ((b5 & 0x0F) << 2))
        unpacked_data[row, 2::4] = (b2 << 6) | ((b5 >> 4) | ((b6 & 0x03) << 4))
        unpacked_data[row, 3::4] = (b3 << 6) | (b6 >> 2)

    return unpacked_data


ROOT = "/data/0324_hnr_cmy_ob_debug/"
INPUT_ROOT = os.path.join(ROOT, "received")
OUTPUT_ROOT = os.path.join(ROOT, "unpack_raw")

# W = 4096
# H = 3600

# W = 4096
# H = 3072

# W = 4000
# H = 2256

W = 4096
H = 2304

STRIDE = 7168
# STRIDE = 8000

os.makedirs(OUTPUT_ROOT, exist_ok=True)

scenes = sorted(
    d for d in os.listdir(INPUT_ROOT)
    if os.path.isdir(os.path.join(INPUT_ROOT, d))
)

for scene in scenes:
    print(f"\n====== 处理场景: {scene} ======")

    scene_in_dir = os.path.join(INPUT_ROOT, scene)
    scene_out_dir = os.path.join(OUTPUT_ROOT, scene)
    os.makedirs(scene_out_dir, exist_ok=True)

    files = sorted(glob.glob(os.path.join(scene_in_dir, "*.RAWMIPI14")))

    if not files:
        print("  未找到 RAWMIPI14 文件，跳过")
        continue

    for file_path in files:
        print(f"  处理文件: {os.path.basename(file_path)}")

        result = unpack_rawmipi14(file_path, W, H, STRIDE)

        out_name = os.path.basename(file_path) + ".raw"
        # out_name = os.path.basename(file_path)

        out_path = os.path.join(scene_out_dir, out_name)

        result.tofile(out_path)

        print(f"  导出: {out_path}")
        print(f"  Max value: {result.max()}")

print("\n全部场景解包完成")
