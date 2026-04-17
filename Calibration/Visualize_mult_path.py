import cv2
import glob
import os
import numpy as np

# =========================
# 原始数据路径
# =========================
ROOT = '/data/MCC_0225/NoiseProfile/4K60_1X_10ms/'

# =========================
# 统一输出路径（重点修改）
# =========================
OUTPUT_ROOT = '/data/MCC_0225/jpg'

# 图像参数
H = 2304
W = 4096

BAYER_PATTERN = 'BGGR'

WP = 16383
BP = 1024

GAMMA = 2.8

DEMOSAIC_DICT = {
    'RGGB': cv2.COLOR_BAYER_BG2BGR_EA,
    'GRBG': cv2.COLOR_BAYER_GB2BGR_EA,
    'GBRG': cv2.COLOR_BAYER_GR2BGR_EA,
    'BGGR': cv2.COLOR_BAYER_RG2BGR_EA
}

# =========================
# 自动遍历所有 scale
# =========================
scales = sorted(os.listdir(ROOT))

for scale in scales:

    scale_dir = os.path.join(ROOT, scale)
    if not os.path.isdir(scale_dir):
        continue

    scenes = sorted(os.listdir(scale_dir))

    for scene in scenes:

        scene_dir = os.path.join(scale_dir, scene)
        if not os.path.isdir(scene_dir):
            continue

        print(f"\nProcessing: {scale}/{scene}")

        # 输出目录改为统一 jpg 根目录
        output_dir = os.path.join(OUTPUT_ROOT, scale, scene)
        os.makedirs(output_dir, exist_ok=True)

        raw_files = sorted(glob.glob(os.path.join(scene_dir, '*.raw')))
        print("Found files:", len(raw_files))

        for file in raw_files:

            img = np.fromfile(file, dtype='uint16')

            if img.size != H * W:
                print("Skip (size mismatch):", file)
                continue

            img = img.reshape([H, W]).astype('float')

            # 归一化
            img = (img - BP) / (WP - BP)
            img = np.clip(img, 0, 1)

            # demosaic
            img = (img * 65535).astype('uint16')
            img = cv2.demosaicing(img, DEMOSAIC_DICT[BAYER_PATTERN])
            img = img.astype('float') / 65535.0

            # 灰度世界 AWB
            eps = 1e-6

            mean_r = img[..., 2].mean()
            mean_g = img[..., 1].mean()
            mean_b = img[..., 0].mean()

            gray = (mean_r + mean_g + mean_b) / 3.0

            gain_r = gray / (mean_r + eps)
            gain_g = gray / (mean_g + eps)
            gain_b = gray / (mean_b + eps)

            img[..., 2] *= gain_r
            img[..., 1] *= gain_g
            img[..., 0] *= gain_b

            # Gamma
            img = np.clip(img, 0, 1)
            img = img ** (1 / GAMMA)

            # 转 8bit
            img = (img * 255).astype('uint8')

            out_name = os.path.basename(file).replace('.raw', '.jpg')
            out_path = os.path.join(output_dir, out_name)

            cv2.imwrite(out_path, img)

            print("Saved:", out_path)

print("\nAll Done.")