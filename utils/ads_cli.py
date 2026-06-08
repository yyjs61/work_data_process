import subprocess, sys, os

# SRC = sys.argv[1]
# DST = sys.argv[2]
# 传输文件  AOSS <----> ECS

# SRC = 's3://isp_projectdata/VideoSupernightData/A500_Benchmark/aitone/OVH9000_DCG_20260318_hair/'
# SRC = 's3://isp_projectdata/VideoSupernightData/IAC4/IAC4_imx01f_EVT2p3_0040_sensor_raw_ultrawide_20260508/'
# SRC = 's3://isp_share/wangyuemei/test_data/hnr_wide_ov52a_dcg_testdate_20260408/'
# SRC = 's3://isp_projectdata/VideoSupernightData/DJI_OV50X/quad_day_20260506/'
# SRC = 's3://isp_projectdata/VideoSupernightData/V3_IMX06C/V3_imx06c_20260509/'
# SRC = 's3://isp_projectdata/VideoSupernightData/8xx/DJI_8xx_3968x2240_20260511/'
# SRC = 's3://liuhaishan-deblur/RM_dump_raw/0508_t1/OnlyEV0/Deblur/output_raw/'
# SRC = 's3://isp_projectdata/VideoSupernightData/V3_IMX06C/V3_imx06c_20260512/'

# SRC = 's3://isp_projectdata/VideoSupernightData/DJI_OV50X/20260513_material/'
# SRC = 's3://isp_projectdata/VideoSupernightData/VNT/IP_V2p5/Test_data_260515/'
# SRC = 's3://isp_projectdata/VideoSupernightData/V3_IMX06C/V3_imx06c_blc_raw_20260522/'
# SRC = 's3://isp_share/wangyuemei/test_data/0525_wide_ov52a_dagquad_texture_testdata2/'
# SRC = 's3://isp_projectdata/Calibration/vnt/IMX832_dgain_calibration_data/'
# SRC = 's3://isp_projectdata/VideoSupernightData/VNT/IP_V2p5/IMX678_Test_data_260521/'
SRC = 's3://isp_projectdata/VideoSupernightData/030/030_1x_dcg_day_highlight_20260604/'

# DST = '/home/user/afs_data/wang/' + os.path.basename(SRC[:-1]) + '/'
# DST = r'D:\Data\DJI_OV50X\20260420\20260417_dcg_lofic/'
# DST = r"D:\Data\2026_05\07\imx01f_EVT2p3_0040\IAC4_imx01f_EVT2p3_0040_sensor_raw_ultrawide_20260508/"
# DST = r"D:\Data\2026_05\0509/output_raw_11/"
# DST = r'D:\Data\2026_05\09\V3_imx06c_20260509/'
# DST = r"D:\Data\2026_05\12\V3_imx06c_20260512/"
# DST = r"D:\Data\DJI_OV50X\20260513\0511_ov50x_raw-2026-05-13\20260513_material/"
# DST = r"D:\Data\2026_05\19\IMX06C_binning_normal_4k_20260514/"
# DST = r"D:\Data\2026_05\20\V3_imx06c_gen_meta_20260520/"
# DST = r"D:\Data\2026_05\20\Cal\IMX832_dgain_calibration_data/"
# DST = r"D:\Data\2026_05\20\Test_data_260520\IMX678_Test_data_260520/"
# DST = r"D:\Data\2026_05\21\IMX678_Test_data_260521/"
# DST = r"D:\Data\2026_05\22\V3_imx06c_20260522/"
# DST = r"C:\Users\admin\Desktop\temp/"
# DST = r"D:\Data\2026_05\26\0525_wide_ov52a_dagquad_texture_testdata2/"
DST = r"D:\Data\2026_06\04\030_1x_dcg_day_highlight_20260604/"

# DST = r'D:\Data\2026_05\07\imx01f_EVT2p3_0040\IAC4_imx01f_EVT2p3_0040_sensor_raw_main_20260508/'


ACCESS = '019CD08AD5FA70418950DF3D777184E0' #ID
SECRET = '019CD08AD5F97EB3B6B69163CF35396D' #key

with open('ROOT_PATH.txt', 'w') as fo:
    fo.write(DST)

# 注释后是 s3-->ecs， 不注释turn
SRC, DST = DST, SRC

if SRC.startswith('s3://'):
    bucket, path = SRC.replace('s3://', '').split('/', 1)
    # src = f's3://{ACCESS}:{SECRET}@{bucket}.aoss-external.cn-sh-01b.sensecoreapi-oss.cn/{path}'
    src = f's3://{ACCESS}:{SECRET}@{bucket}.aoss.cn-sh-01b.sensecoreapi-oss.cn/{path}'
    subprocess.Popen(f'ads-cli --threads 20 sync {src} {DST} ', shell=True)
if DST.startswith('s3://'):
    bucket, path = DST.replace('s3://', '').split('/', 1)
    # dst = f's3://{ACCESS}:{SECRET}@{bucket}.aoss-external.cn-sh-01b.sensecoreapi-oss.cn/{path}'
    dst = f's3://{ACCESS}:{SECRET}@{bucket}.aoss.cn-sh-01b.sensecoreapi-oss.cn/{path}'
    subprocess.Popen(f'ads-cli --threads 20 sync {SRC} {dst} ', shell=True)







