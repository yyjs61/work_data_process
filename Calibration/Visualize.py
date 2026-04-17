import os
import cv2
import numpy as np

ROOT = "/data/0228_cal"

RAW_ROOT = os.path.join(ROOT, "NoiseProfile")
OUT_ROOT = os.path.join(ROOT, "jpg")

W = 3840
H = 2160

BIT_DEPTH = 12
BP = 256
WP = 4095

GAMMA = 2.8
isp_gain = 1.0

eps = 1e-6

os.makedirs(OUT_ROOT, exist_ok=True)

# ===== 递归遍历所有子目录 =====
for root, _, files in os.walk(RAW_ROOT):

    raw_files = [f for f in files if f.lower().endswith(".raw")]
    if not raw_files:
        continue

    # 保持目录结构
    rel_path = os.path.relpath(root, RAW_ROOT)
    out_dir = os.path.join(OUT_ROOT, rel_path)
    os.makedirs(out_dir, exist_ok=True)

    print(f"\n处理目录: {root}")

    for raw_name in sorted(raw_files):

        raw_path = os.path.join(root, raw_name)

        if os.path.getsize(raw_path) == 0:
            print(f"{raw_path} 大小为0，跳过")
            continue

        raw = np.fromfile(raw_path, np.uint16)

        if raw.size != H * W:
            print(f"{raw_path} 尺寸不匹配，跳过")
            continue

        img = raw.reshape(H, W).astype(np.float32)

        # normalize
        img = (img - BP) / (WP - BP)
        img = img.clip(0.0, 1.0)

        # RGGB
        r  = img[0::2, 0::2]
        g0 = img[0::2, 1::2]
        g1 = img[1::2, 0::2]
        b  = img[1::2, 1::2]

        g = (g0 + g1) / 2.0
        img_rgb = np.stack([b, g, r], axis=-1)

        # auto white balance
        mean_r = img_rgb[..., 2].mean()
        mean_g = img_rgb[..., 1].mean()
        mean_b = img_rgb[..., 0].mean()

        gray = (mean_r + mean_g + mean_b) / 3.0

        gain_r = gray / (mean_r + eps)
        gain_g = gray / (mean_g + eps)
        gain_b = gray / (mean_b + eps)

        img_rgb[..., 2] *= gain_r
        img_rgb[..., 1] *= gain_g
        img_rgb[..., 0] *= gain_b

        img_rgb *= isp_gain
        img_rgb = img_rgb.clip(0.0, 1.0)

        img_rgb = img_rgb ** (1.0 / GAMMA)

        img_out = (img_rgb.clip(0.0, 1.0) * 255).astype(np.uint8)

        out_name = raw_name.replace(".raw", ".jpg")
        cv2.imwrite(os.path.join(out_dir, out_name), img_out)

print("\n全部转换完成")