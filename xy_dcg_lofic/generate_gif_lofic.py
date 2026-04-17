import os
import glob
import subprocess

ROOT = "/data/ov50x/"
JPG_ROOT = os.path.join(ROOT, "jpg")
GIF_ROOT = os.path.join(ROOT, "gif")

FPS = 10
SCALE_W = 768

os.makedirs(GIF_ROOT, exist_ok=True)

for scene in sorted(os.listdir(JPG_ROOT)):
    scene_path = os.path.join(JPG_ROOT, scene)
    if not os.path.isdir(scene_path):
        continue

    for kind in ["long", "short"]:
        jpgs = sorted(glob.glob(os.path.join(scene_path, f"*__{kind}.jpg")))
        if not jpgs:
            continue

        frames_txt = os.path.join(scene_path, f"frames_{kind}.txt")
        palette_png = os.path.join(scene_path, f"palette_{kind}.png")
        gif_name = f"{scene}_{kind}.gif"
        gif_path = os.path.join(GIF_ROOT, gif_name)

        # 写 concat 文件
        with open(frames_txt, "w") as f:
            for jpg in jpgs:
                f.write(f"file '{jpg}'\n")

        try:
            print(f"[Processing] {gif_name}")

            # Step1: 生成调色板（强制像素格式）
            subprocess.run([
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", frames_txt,
                "-vf",
                f"fps={FPS},scale={SCALE_W}:-1:flags=lanczos,"
                "format=yuv420p,setsar=1,"
                "palettegen=stats_mode=diff",
                palette_png
            ], check=True)

            # Step2: 生成GIF（强制像素格式）
            subprocess.run([
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", frames_txt,
                "-i", palette_png,
                "-lavfi",
                f"fps={FPS},scale={SCALE_W}:-1:flags=lanczos,"
                "format=yuv420p[x];[x][1:v]paletteuse=dither=sierra2_4a",
                "-loop", "0",
                gif_path
            ], check=True)

            print(f"[OK] {gif_name}")

        except subprocess.CalledProcessError as e:
            print(f"[FAILED] {gif_name}")
            print(e)

        finally:
            if os.path.exists(frames_txt):
                os.remove(frames_txt)
            if os.path.exists(palette_png):
                os.remove(palette_png)
