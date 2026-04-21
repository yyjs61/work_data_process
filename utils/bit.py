import numpy as np

# path = '/home/user/afs_data/LeeSin_Xie/quadraw_for_yw_20260408/unpack_raw/00__20000105_053403_offline_dump/000__MF_0.raw'
path = r'D:\Data\DJI_OV50X\20260420\20260417_dcg_lofic\unpack_raw\00__20251209_203817-10p00ms-15p62x_8p00x-1p00x_1p00x-m11\001__0000_0.raw'
# path = r'D:\Data\DJI_OV50X\dji_pkt_ov50x_dcg_lofic_20260209\unpack_raw\00__scene1\001__short.raw'
img = np.fromfile(path, np.uint16)

print(np.max(img))
print(np.sum(img & 0b11))