import os
import subprocess
import glob

# ROOT = "/home/user/afs_data/wang/hnr_wide_ov52a_dcg_testdate_20260408"
# ROOT = r"D:\Data\DJI_OV50X\20260422\flower_portrait_20260422-2026-04-22\Quad_dag_20260422/"
# ROOT = r'D:\Data\20260423\VAI_OVH9000_Magic7Pro_20260423/'
# ROOT = r'D:\Data\2026_04\29\OVH9000_DCG_20260429_garage/'
# ROOT = r'D:\Data\2026_05\06\V3_imx06c_20260506/'
# ROOT = r"D:\Data\DJI_OV50X\20260506\v2_data_20260506-2026-05-06\v2_data_20260506/"
ROOT = r'D:\Data\2026_05\07\add_/'


# ROOT = "/home/user/afs_data/LeeSin_Xie/quadraw_for_yw_20260408"

JPG_ROOT = os.path.join(ROOT, "jpg")
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