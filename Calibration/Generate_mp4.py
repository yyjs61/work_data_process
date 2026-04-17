import os
import subprocess
import glob

# 读取根目录
# ROOT_PATH_FILE = './ROOT_PATH.txt'
# with open(ROOT_PATH_FILE, 'r') as f:
#     ROOT = f.readline().strip()

ROOT = '/data/0319_wide_ov52a_dcg_er15_word_testData'

JPG_ROOT = os.path.join(ROOT, "jpg")
MP4_ROOT = os.path.join(ROOT, "mp4")

os.makedirs(MP4_ROOT, exist_ok=True)

for group in sorted(os.listdir(JPG_ROOT)):
    group_path = os.path.join(JPG_ROOT, group)
    if not os.path.isdir(group_path):
        continue

    jpgs = sorted(glob.glob(os.path.join(group_path, "*.jpg")))
    if not jpgs:
        print(f"[SKIP] {group} 没有 JPG 图片")
        continue

    frames_txt = os.path.join(group_path, "frames.txt")
    mp4_path = os.path.join(MP4_ROOT, f"{group}.mp4")

    # 生成图片列表文件（供 ffmpeg concat 使用）
    with open(frames_txt, "w") as f:
        for jpg in jpgs:
            f.write(f"file '{jpg}'\n")

    try:
        # 调用 ffmpeg 合成 MP4
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", frames_txt,
            "-vf", "fps=10,scale=768:-1:flags=lanczos",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            "-crf", "23",
            mp4_path
        ], check=True)

        print(f"[OK] {group} -> {mp4_path}")

    finally:
        # 清理临时文件
        if os.path.exists(frames_txt):
            os.remove(frames_txt)