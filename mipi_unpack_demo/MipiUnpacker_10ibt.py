import ctypes, glob, os, sys

def rawPreprocess(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth, in_filepath, out_filepath):
    lib = ctypes.cdll.LoadLibrary('/home/user/code/data_process_demo/mipi_unpack_demo/libMipiUnpacker.so')
    # lib = ctypes.windll.LoadLibrary('./data_process_demo/mipi_unpack_demo/libMipiUnpacker.dll')  # use this if run on Win64
    # lib = ctypes.windll.LoadLibrary('./src/MipiUnpacker_last.dll')  # use this if run on Win64
    in_filepath_c_str = ctypes.c_char_p(bytes(in_filepath, 'utf-8'))
    out_filepath_c_str = ctypes.c_char_p(bytes(out_filepath, 'utf-8'))
    lib.mipiUnpacker(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth, in_filepath_c_str, out_filepath_c_str)

# code below is used for preprocessing a scene (parallel for scenes)
if __name__ == '__main__':

    height = 2160
    width = 3840  # 12bit --> 10bit
    stride = 4800
    in_pack_bit_depth = 10
    out_unpack_bit_depth = 10
    # out_unpack_bit_depth = 14

    # ROOT_PATH = './ROOT_PATH.txt'
    # with open(ROOT_PATH,'r') as file:
    #     ROOT = file.readline().strip()

    # MIPI_RAW = os.path.join(ROOT,'mipi_raw')
    # UNPACK_RAW = os.path.join(ROOT,'unpack_raw2')
    # scenes = sorted(os.listdir(MIPI_RAW))

    ROOT = '/data/BlackLevel/origin/'
    RECEIVED = ROOT + 'BlackLevel'
    tag = 'unpack_raw'
    scenes = glob.glob(os.path.join(RECEIVED, '*'))
    # scenes = ['/data/Testdata_20251211/received/indoorstate4_snapdragon']
    os.makedirs(os.path.join(ROOT, tag), exist_ok= True)
    for scene in sorted(scenes):
        scene_name = os.path.basename(scene)
        out_scene_dir = os.path.join(ROOT, tag, scene_name)
        os.makedirs(out_scene_dir, exist_ok=True)
        file_tag = '*.raw'
        # file_tag = '*.RAWMIPI10'
        file_paths = sorted(glob.glob(os.path.join(scene, file_tag)))
        for file_path in file_paths:
            if os.path.getsize(file_path) == 0:
                print(f'{file_path}的数据大小为0，跳过')
                continue
            # out_path = os.path.join(ROOT, tag, os.path.basename(scene), os.path.basename(file_path) + '.raw')
            out_path = os.path.join(ROOT, tag, os.path.basename(scene), os.path.basename(file_path))
            rawPreprocess(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth,
                        file_path, out_path)