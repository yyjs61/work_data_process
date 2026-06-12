import os
import subprocess
import glob

# ROOT = "/home/user/afs_data/wang/hnr_wide_ov52a_dcg_testdate_20260408"
# ROOT = r"D:\Data\DJI_OV50X\20260422\flower_portrait_20260422-2026-04-22\Quad_dag_20260422/"
# ROOT = r'D:\Data\20260423\VAI_OVH9000_Magic7Pro_20260423/'
# ROOT = r'D:\Data\2026_04\29\OVH9000_DCG_20260429_garage/'
# ROOT = r'D:\Data\2026_05\06\V3_imx06c_20260506/'
# ROOT = r"D:\Data\DJI_OV50X\20260506\v2_data_20260506-2026-05-06\v2_data_20260506/"
# ROOT = r'D:\Data\2026_05\07\add_/'
# ROOT = r'D:\Data\2026_05\07\imx01f_EVT2p3_0040\IAC4_imx01f_EVT2p3_0040_sensor_raw_ultrawide_20260508/'
# ROOT = r'D:\Data\2026_05\08\D-gain_calibration_data/'

# ROOT = r"D:\Data\2026_05\09\V3_imx06c_20260509/"
# ROOT = r"D:\Data\DJI_OV50X\20260509\Quad_dag_20260509"
# ROOT = r"D:\Data\2026_05\12\V3_imx06c_20260512/"
# ROOT = r'E:\0512/'
# ROOT = r'D:\Data\2026_05\19\0519/'
# ROOT = r'D:\Data\2026_05\19\IMX06C_binning_normal_4k_20260514/'
# ROOT = r"D:\Data\2026_05\20\V3_imx06c_gen_meta_20260520/"
# ROOT = r"D:\Data\2026_05\20\V3_imx06c_20260520/"
# ROOT = r"D:\Data\2026_05\22\V3_imx06c_20260522/"
# ROOT = r"D:\Data\2026_05\22\blc_raw/"
# ROOT = r'D:\Data\2026_05\22\IAC4_IMX01F_DCG_ER4_UltralWide_20260522/'
# ROOT = r'D:\Data\2026_05\25\IAC4_IMX01F_DCG_ER4_Wide_night_20260525/'
# ROOT = r"D:\Data\2026_05\26\0525_wide_ov52a_dagquad_texture_testdata2/"
# ROOT = r'D:\Data\2026_05\27\IAC4_IMX01F_DCG_ER16_Wide_Night_dumpraw_20260527/'
# ROOT = r'D:\Data\2026_05\28\IAC4_IMX01F_DCG_ER16_01_20260528/'
# ROOT = r'D:\Data\2026_05\29\NR_iterative_data_20260529/'
# ROOT = 'D:/Data/2026_06/01/030_20260601_day_dump/'
# ROOT = r'D:\Data\2026_06\03\IAC4_IMX01F_DCG_ER4_Wide_20260603/'
# ROOT = r'D:\Data\2026_06\04\030_4k60_quad_scg_outside_20260604/'
# ROOT = r"D:\Data\2026_06\05\20260604_2x_4k60_raw\030_4k60_quad_scg_day_20260605/"
# ROOT = r'D:\Data\2026_06\05\V210_OV50X_quad_night_20260519/'
# ROOT = r"D:\Data\2026_06\05\030_1x_dcg_sensor_raw_ev0_ev+_ev+2_3000k_20260605/"
# ROOT = r"D:\Data\2026_06\05\030_2x_4k30_quad_dcg_day_20260605/"
# ROOT = r"D:\Data\2026_06\08\Honor_FPRO_TELE_QUAD_20260608_ER1/"
# ROOT = r'D:\Data\2026_06\09\iac4\IAC4_IMX01F_DCG_ER4_Wide_out_20260609/'
# ROOT = r'D:\Data\2026_06\09\V3_imx01f_20260609/'
# ROOT = r'D:\Data\2026_06\09\IAC4_IMX01F_DCG_ER4_Wide_lab_20260609/'
# ROOT = r"D:\Data\2026_06\10\030_4k60_quad_scg_20260610/"
# ROOT = r"D:\Data\2026_06\10\ainr_MCC_BLC/"
# ROOT = r"D:\Data\2026_06\10\SC532_SCG_10bit_ISP_simulation_demo_raw_20260610/"
ROOT = r"D:\Data\2026_06\11\HY_IMX06A_20260601/"

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