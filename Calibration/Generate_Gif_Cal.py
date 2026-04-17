import os
import glob
import subprocess

ROOT = "/data/030_CALI_9_16_0326/"

JPG_ROOT = os.path.join(ROOT, "jpg")
GIF_ROOT = os.path.join(ROOT, "gif")

FPS = 10
SCALE_W = 768

os.makedirs(GIF_ROOT, exist_ok=True)

for module in sorted(os.listdir(JPG_ROOT)):
    module_path = os.path.join(JPG_ROOT, module)

    for scale in sorted(os.listdir(module_path)):
        scale_path = os.path.join(module_path, scale)

        jpgs = sorted(glob.glob(os.path.join(scale_path, "*.jpg")))
        frames_txt = os.path.join(scale_path, "frames.txt")
        palette_png = os.path.join(scale_path, "palette.png")

        gif_name = f"{module}_{scale}.gif"          
        gif_path = os.path.join(GIF_ROOT, gif_name)

        with open(frames_txt, "w") as f:
            for jpg in jpgs:
                f.write(f"file '{jpg}'\n")

        try:
            subprocess.run([
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", frames_txt,
                "-vf",
                f"fps={FPS},scale={SCALE_W}:-1:flags=lanczos,"
                "palettegen=stats_mode=diff",
                palette_png
            ], check=True)

            subprocess.run([
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", frames_txt,
                "-i", palette_png,
                "-filter_complex",
                f"fps={FPS},scale={SCALE_W}:-1:flags=lanczos[x];"
                "[x][1:v]paletteuse=dither=sierra2_4a",
                "-loop", "0",
                gif_path
            ], check=True)

            print(f"[OK] {gif_name}")

        finally:
            if os.path.exists(frames_txt):
                os.remove(frames_txt)
            if os.path.exists(palette_png):
                os.remove(palette_png)
