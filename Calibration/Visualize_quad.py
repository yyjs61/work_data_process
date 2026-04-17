import os
import cv2
import numpy as np
from glob import glob

ROOT = "/home/user/afs_data/LeeSin_Xie/8xx/DJI_8xx_20260408_标定数据"

RAW_ROOT = os.path.join(ROOT, "NoiseProfile")
OUT_ROOT = os.path.join(ROOT, "jpg", "NoiseProfile")
# RAW_ROOT = os.path.join(ROOT, "BlackLevel")
# OUT_ROOT = os.path.join(ROOT, "jpg", "BlackLevel")

# Quad RAW 尺寸（unpack 后）
W = 4096
H = 2304


# BP = 64
# WP = 1023

# BP = 256
# WP = 4095
BP = 64
WP = 4095

# BP = 1024
# WP = 16383

GAMMA = 2.8

os.makedirs(OUT_ROOT, exist_ok=True)

def quad_bggr_to_rgb(img):
    """
    Quad BGGR → RGB (H/2, W/2, 3)
    """
    # 每个 2x2 是同色，直接取均值
    img_q = img.reshape(H//2, 2, W//2, 2).mean(axis=(1, 3))

    # Quad BGGR 映射
    b = img_q[0::2, 0::2]
    g0 = img_q[0::2, 1::2]
    g1 = img_q[1::2, 0::2]
    r = img_q[1::2, 1::2]

    g = (g0 + g1) * 0.5
    rgb = np.stack([r, g, b], axis=-1)
    return rgb


for scene in sorted(os.listdir(RAW_ROOT)):
    scene_path = os.path.join(RAW_ROOT, scene)
    out_scene = os.path.join(OUT_ROOT, scene)
    os.makedirs(out_scene, exist_ok=True)

    raws = sorted(glob(os.path.join(scene_path, "*.raw")))

    for raw_path in raws:
        raw = np.fromfile(raw_path, np.uint16)
        img = raw.reshape(H, W).astype(np.float32)

        # Black / White normalize
        img = (img - BP) / (WP - BP)
        img = img.clip(0.0, 1.0)

        # Quad → RGB
        rgb = quad_bggr_to_rgb(img)

        # Gamma（仅用于看）
        rgb = rgb ** (1.0 / GAMMA)
        rgb = (rgb.clip(0.0, 1.0) * 255).astype(np.uint8)

        out_name = os.path.basename(raw_path).replace(".raw", ".jpg")
        cv2.imwrite(os.path.join(out_scene, out_name), rgb)

    print(f"[OK] {scene}")
