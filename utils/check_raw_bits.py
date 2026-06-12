import numpy as np

# path = r'D:\Data\2026_05\29\Competitor_data_260529\NROut_0p5lux_raw\NROut_0p5lux_raw\NR_OUT_0p5lux_000.raw'
# path = r'D:\Data\2026_06\09\V3_imx01f_20260609\unpack_raw\00__0528_01f_gain11p18\008__10943.raw'
# path = r'D:\Data\2026_06\09\V3_imx01f_20260609\unpack_raw\02__v040072_qh007_day_pushin\000__152.raw'
path = r'D:\Data\2026_06\11\HY_IMX06A_20260601\HY_IMX06A_20260611\NoiseProfile\A_gain_1_3583\RAW_3840x2160_12bits_RGGB_Linear_20260608111842_03.raw'
img = np.fromfile(path, dtype=np.uint16)

# imgs[0].tofile('a.raw')
masks = [
	(0x1, "最低位 (LSB)"),
	(0x3, "低2位"),
	(0x7, "低3位"), 
	(0xF, "低4位"),
	(0xFF, "低8位"),
	(0xFFF, "低12位"),
	(0xFFFF, "全部16位")
]


print(img.max(), img.min())
for m, dsc in masks:
	print(dsc)
	print((img & m).max())

n_pixels = len(img)

print(f"总像素数: {n_pixels}")
print("位序号 (0 = LSB, 15 = MSB) | 全零? | 为1的比例")
print("-" * 45)
print('max min', img.max(),img.mean(), img.min())
for bit in range(16):
	
	bit_values = (img >> bit) & 1
	ones = np.sum(bit_values)
	is_all_zero = (ones == 0)

	ratio = ones / n_pixels * 100
	print(f"bit {bit:2d}                       | {'yes' if is_all_zero else 'no'}     | {ratio:6.2f}%")