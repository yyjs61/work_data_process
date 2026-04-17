import os
import subprocess
import glob

ROOT = "/data/HNR_ov52a_dag_quad_20260325/"
JPG_ROOT = os.path.join(ROOT, "jpg")
GIF_ROOT = os.path.join(ROOT, "gif")

os.makedirs(GIF_ROOT, exist_ok=True)

# =========================
# 遍历 scale
# =========================
for scale in sorted(os.listdir(JPG_ROOT)):

    scale_path = os.path.join(JPG_ROOT, scale)
    if not os.path.isdir(scale_path):
        continue

    # =========================
    # 遍历 scene
    # =========================
    for scene in sorted(os.listdir(scale_path)):

        group_path = os.path.join(scale_path, scene)
        if not os.path.isdir(group_path):
            continue

        group_name = f"{scale}_{scene}"

        jpgs = sorted(glob.glob(os.path.join(group_path, "*.jpg")))
        if len(jpgs) == 0:
            print(f"[SKIP] {group_name} no jpg")
            continue

        frames_txt = os.path.join(group_path, "frames.txt")
        palette_png = os.path.join(group_path, "palette.png")
        gif_path = os.path.join(GIF_ROOT, f"{group_name}.gif")

        # 生成 frames.txt
        with open(frames_txt, "w") as f:
            for jpg in jpgs:
                f.write(f"file '{jpg}'\n")

        try:
            # 生成调色板
            subprocess.run([
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", frames_txt,
                "-vf",
                "fps=10,scale=768:-1:flags=lanczos,palettegen=stats_mode=diff",
                palette_png
            ], check=True)

            # 生成 GIF
            subprocess.run([
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", frames_txt,
                "-i", palette_png,
                "-filter_complex",
                "fps=10,scale=768:-1:flags=lanczos[x];"
                "[x][1:v]paletteuse=dither=sierra2_4a",
                "-loop", "0",
                gif_path
            ], check=True)

            print(f"[OK] {group_name} -> {gif_path}")

        finally:
            if os.path.exists(frames_txt):
                os.remove(frames_txt)
            if os.path.exists(palette_png):
                os.remove(palette_png)