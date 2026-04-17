import os
import glob
import shutil
import natsort

ROOT_PATH = './ROOT_PATH.txt'
with open(ROOT_PATH, 'r') as f:
    ROOT = f.readline().strip()

RECEIVED = os.path.join(ROOT, 'received')
UNPACK_RAW = os.path.join(ROOT, 'unpack_raw')

RAW_FILE_SIZE = 16588800  

scenes = natsort.natsorted(os.listdir(RECEIVED))

for scene_id, scene in enumerate(scenes):
    scene_path = os.path.join(RECEIVED, scene)
    if not os.path.isdir(scene_path):
        continue

    # 一级目录：00__5 或 01__6
    out_scene_dir = os.path.join(UNPACK_RAW, f"{str(scene_id).zfill(2)}__{scene.replace(' ', '_').replace(',', '_').replace('.', 'p')}")
    os.makedirs(out_scene_dir, exist_ok=True)

    # 遍历 scene 下的子文件夹（例如 normal_19700102_004545_519933_Session_2_cam2）
    subfolders = [f for f in natsort.natsorted(os.listdir(scene_path)) if os.path.isdir(os.path.join(scene_path, f))]
    if len(subfolders) == 0:
        # 如果没有子文件夹，直接在一级目录下放 raw
        subfolders = ['.']

    for sub_id, subfolder in enumerate(subfolders):
        if subfolder == '.':
            out_dir = out_scene_dir
            subfolder_path = scene_path
        else:
            out_dir = os.path.join(out_scene_dir, f"{str(sub_id).zfill(2)}__{subfolder.replace(' ', '_').replace(',', '_').replace('.', 'p')}")
            subfolder_path = os.path.join(scene_path, subfolder)

        os.makedirs(out_dir, exist_ok=True)

        # 找到所有 raw 文件
        raw_files = glob.glob(os.path.join(subfolder_path, '**', '*.raw'), recursive=True)
        raw_files = natsort.natsorted([f for f in raw_files if os.path.getsize(f) == RAW_FILE_SIZE])

        for i, raw_file in enumerate(raw_files):
            new_name = os.path.join(out_dir, f"{str(i).zfill(3)}_{os.path.basename(raw_file)}")
            shutil.move(raw_file, new_name)

        print(f"[Done] Moved {len(raw_files)} raw files to {out_dir}")

