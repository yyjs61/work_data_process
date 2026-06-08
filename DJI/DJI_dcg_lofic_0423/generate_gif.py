import os
import subprocess
import glob

# ROOT = r"D:\Data\DJI_OV50X\20260423\20260423_Simulation_materials/"
ROOT = r"D:\Data\DJI_OV50X\20260513\0511_ov50x_raw-2026-05-13\20260513_material/"

JPG_ROOT = os.path.join(ROOT, "jpg")
GIF_ROOT = os.path.join(ROOT, "gif")
os.makedirs(GIF_ROOT, exist_ok=True)



def process_gif(group, jpgs, suffix, GIF_ROOT): 
    """处理并生成 gif"""
    frames_txt = os.path.join(GIF_ROOT, f"{group}_{suffix}_frames.txt")
    palette_png = os.path.join(GIF_ROOT, f"{group}_{suffix}_palette.png")
    gif_path = os.path.join(GIF_ROOT, f"{group}__{suffix}.gif")
    
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
        
        # 生成 gif
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
        
        print(f"[OK] {group}__{suffix} -> {gif_path} ({len(jpgs)} frames)")
    
    finally:
        if os.path.exists(frames_txt):
            os.remove(frames_txt)
        if os.path.exists(palette_png):
            os.remove(palette_png)


for group in sorted(os.listdir(JPG_ROOT)):
    group_path = os.path.join(JPG_ROOT, group)
    if not os.path.isdir(group_path):
        continue
    
    # 获取所有 jpg 文件
    all_jpgs = sorted(glob.glob(os.path.join(group_path, "*.jpg")))
    
    if len(all_jpgs) == 0:
        print(f"[SKIP] {group} no jpg")
        continue
    
    # 根据后缀分类（short 和 lofic）
    short_jpgs = [jpg for jpg in all_jpgs if '__short.jpg' in jpg]
    lofic_jpgs = [jpg for jpg in all_jpgs if '__long.jpg' in jpg]
    
    # 处理 short 类型
    if short_jpgs:
        process_gif(group, short_jpgs, "short", GIF_ROOT)
    else:
        print(f"[WARN] {group} 没有找到 short 类型的 jpg")
    
    # 处理 lofic 类型
    if lofic_jpgs:
        process_gif(group, lofic_jpgs, "long", GIF_ROOT)
    else:
        print(f"[WARN] {group} 没有找到 long 类型的 jpg")            