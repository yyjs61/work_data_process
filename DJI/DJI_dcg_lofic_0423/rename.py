import os
import glob
import natsort
# ROOT = '/home/user/afs_data/0327_wide_ov52a_dagquad_testdata/unpack_raw/'
# ROOT = '/home/user/afs_data/LeeSin_Xie/quadraw_for_yw_20260408/unpack_raw/'
ROOT = r"D:\Data\DJI_OV50X\20260420\20260417_portrait/unpack_raw/"

# 注意下面 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# 获取当前场景文件夹列表并排序
scenes = natsort.natsorted(os.listdir(ROOT))

for idx, scene_name in enumerate(scenes):
    old_path = os.path.join(ROOT, scene_name)
    if not os.path.isdir(old_path):
        continue

    prefix = f"{idx:02d}__"
    new_name = prefix + scene_name
    new_path = os.path.join(ROOT, new_name)
    os.rename(old_path, new_path)
    print(f"{old_path} -> {new_path}")

import os
import glob
import natsort

# ROOT = "/home/user/afs_data/LeeSin_Xie/quadraw_for_yw_20260408/unpack_raw"
ROOT = r"D:\Data\DJI_OV50X\20260420\20260417_portrait/unpack_raw/"

scenes = natsort.natsorted(os.listdir(ROOT))

for scene in scenes:

    scene_dir = os.path.join(ROOT, scene)

    if not os.path.isdir(scene_dir):
        continue

    raw_files = glob.glob(os.path.join(scene_dir, "*.raw"))

    if len(raw_files) == 0:
        continue

    # 自然排序
    raw_files = natsort.natsorted(raw_files)

    print(f"{scene}: {len(raw_files)} raws")

    for i, raw in enumerate(raw_files):

        filename = os.path.basename(raw)

        new_name = f"{i:03d}__{filename}"
        new_path = os.path.join(scene_dir, new_name)

        os.rename(raw, new_path)

    print(scene, "prefix added")
