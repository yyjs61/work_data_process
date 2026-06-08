import os
import subprocess
import glob

# 读取根目录
# ROOT_PATH_FILE = './ROOT_PATH.txt'
# with open(ROOT_PATH_FILE, 'r') as f:
#     ROOT = f.readline().strip()

# ROOT = "/home/user/afs_data/LeeSin_Xie/quadraw_for_yw_20260408"
# ROOT = r"D:\Data\DJI_OV50X\20260422\flower_portrait_20260422-2026-04-22\Quad_dag_20260422/"
# ROOT = r"D:\Data\DJI_OV50X\20260506\v2_data_20260506-2026-05-06\quad_day_20260506/"
# ROOT = r'D:\Data\2026_05\07\add_/'

# ROOT = r"D:\Data\2026_05\09\V3_imx06c_20260509/"
# ROOT = r"D:\Data\DJI_OV50X\20260509\Quad_dag_20260509"
# ROOT = r"D:\Data\2026_05\12\V3_imx06c_20260512/"
# ROOT = r'D:\Data\2026_05\19\IMX06C_binning_normal_4k_20260514/'
# ROOT = r"D:\Data\2026_05\20\V3_imx06c_gen_meta_20260520/"
# ROOT = r'D:\Data\2026_05\22\IAC4_IMX01F_DCG_ER4_UltralWide_20260522/'
# ROOT = r'D:\Data\2026_05\25\IAC4_IMX01F_DCG_ER4_Wide_night_20260525/'
# ROOT = r"D:\Data\2026_05\26\0525_wide_ov52a_dagquad_texture_testdata2/"
# ROOT = r'D:\Data\2026_05\28\IAC4_IMX01F_DCG_ER16_Wide_20260528/'
# ROOT = r'D:\Data\2026_06\IAC4_IMX01F_DCG_ER4_Wide_Night_dumpraw_20260601/'
# ROOT = r'D:\Data\2026_06\03\IAC4_IMX01F_DCG_ER4_Wide_20260603/'
# ROOT = r'D:\Data\2026_06\04\030_4k60_quad_scg_outside_20260604/'
# ROOT = r"D:\Data\2026_06\05\20260604_2x_4k60_raw\030_4k60_quad_scg_day_20260605/"
# ROOT = r"D:\Data\2026_06\05\030_2x_4k30_quad_dcg_day_20260605/"
ROOT = r'D:\Data\2026_06\07\IAC4_IMX01F_DCG_ER4_Wide_move_20260608/'
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

    # try:
    #     # 调用 ffmpeg 合成 MP4
    #     subprocess.run([
    #         "ffmpeg", "-y",
    #         "-f", "concat", "-safe", "0",
    #         "-i", frames_txt,
    #         "-vf", "fps=10,scale=768:-1:flags=lanczos",
    #         "-c:v", "libx264",
    #         "-pix_fmt", "yuv420p",
    #         "-preset", "medium",
    #         "-crf", "23",
    #         mp4_path
    #     ], check=True)

    #     print(f"[OK] {group} -> {mp4_path}")

    # finally:
    #     # 清理临时文件
    #     if os.path.exists(frames_txt):
    #         os.remove(frames_txt)

    # ... 前面代码不变 ...

    try:
        # 调用 ffmpeg 合成 MP4
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", frames_txt,
            "-vf", "fps=10,scale=768:-2:flags=lanczos",  # 👈 关键修改：-1 → -2
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            "-crf", "23",
            mp4_path
        ], check=True, capture_output=True, text=True)  # 👈 建议添加：捕获输出便于调试

        print(f"[OK] {group} -> {mp4_path}")

    except subprocess.CalledProcessError as e:
        # 👈 添加错误处理，打印 ffmpeg 详细输出
        print(f"[ERROR] {group} 合成失败:")
        print(e.stderr)
        raise
    finally:
        # 清理临时文件
        if os.path.exists(frames_txt):
            os.remove(frames_txt)