import subprocess, sys, os

# SRC = sys.argv[1]
# DST = sys.argv[2]
# 传输文件  AOSS <----> ECS

# SRC = 's3://isp_projectdata/VideoSupernightData/A500_Benchmark/aitone/OVH9000_DCG_20260318_hair/'
SRC = 's3://isp_projectdata/VideoSupernightData/DJI_OV50X/20260417_dcg_lofic/'
# SRC = 's3://isp_share/wangyuemei/test_data/hnr_wide_ov52a_dcg_testdate_20260408/'


# DST = '/home/user/afs_data/wang/' + os.path.basename(SRC[:-1]) + '/'
DST = r'D:\Data\DJI_OV50X\20260420\20260417_dcg_lofic/'


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







