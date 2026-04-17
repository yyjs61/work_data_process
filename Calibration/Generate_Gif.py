import os
import subprocess
import glob

# ROOT = "/data/Swan_imx906_testdata_20260329"
ROOT = "/home/user/afs_data/LeeSin_Xie/data/RatingData"
JPG_ROOT = os.path.join(ROOT, "jpg", "BlackLevel")
GIF_ROOT = os.path.join(ROOT, "gif")

os.makedirs(GIF_ROOT, exist_ok=True)

for group in sorted(os.listdir(JPG_ROOT)):
    group_path = os.path.join(JPG_ROOT, group)
    if not os.path.isdir(group_path):
        continue

    jpgs = sorted(glob.glob(os.path.join(group_path, "*.jpg")))
    if len(jpgs) == 0:
        print(f"[SKIP] {group} no jpg")
        continue

    frames_txt = os.path.join(group_path, "frames.txt")
    palette_png = os.path.join(group_path, "palette.png")
    gif_path = os.path.join(GIF_ROOT, f"{group}.gif")

    with open(frames_txt, "w") as f:
        for jpg in jpgs:
            f.write(f"file '{jpg}'\n")

    try:
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", frames_txt,
            "-vf",
            "fps=10,scale=768:-1:flags=lanczos,palettegen=stats_mode=diff",
            palette_png
        ], check=True)

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

        print(f"[OK] {group} -> {gif_path}")

    finally:
        if os.path.exists(frames_txt):
            os.remove(frames_txt)
        if os.path.exists(palette_png):
            os.remove(palette_png)
