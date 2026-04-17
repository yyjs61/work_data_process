import numpy as np

# path = '/home/user/afs_data/LeeSin_Xie/quadraw_for_yw_20260408/unpack_raw/00__20000105_053403_offline_dump/000__MF_0.raw'
path = r'D:\Data\DJI_OV50X\dji_pkt_ov50x_dcg_lofic_20260209\backup\00__scene1\000__long.raw'
# path = r'D:\Data\DJI_OV50X\dji_pkt_ov50x_dcg_lofic_20260209\unpack_raw\00__scene1\001__short.raw'
img = np.fromfile(path, np.uint16)

print(np.max(img))
print(np.sum(img & 0b11))