# import ctypes, glob, os, sys

# def rawPreprocess(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth, in_filepath, out_filepath):
#     # lib = ctypes.cdll.LoadLibrary('./libs/libSequentialUnpacker.so')
#     lib = ctypes.windll.LoadLibrary('./libSequentialUnpacker.dll')  # use this if run on Win64
#     in_filepath_c_str = ctypes.c_char_p(bytes(in_filepath, 'utf-8'))
#     out_filepath_c_str = ctypes.c_char_p(bytes(out_filepath, 'utf-8'))
#     lib.sequentialUnpacker(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth, in_filepath_c_str, out_filepath_c_str)

# # code below is used for preprocessing a scene (parallel by scenes)
# if __name__ == '__main__':
#     files = sorted(glob.glob('*.raw'))
#     for file in files:
#         # rawPreprocess(3072, 4096, 7168, 14, 14, file, 'unpacked__' + file)
#         rawPreprocess(4912, 8192, 10240, 10, 10, file, 'unpacked__' + file)

import ctypes, glob, os, sys

def rawPreprocess(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth, in_filepath, out_filepath):
    # lib = ctypes.cdll.LoadLibrary('libSequentialUnpacker.so')
    # lib = ctypes.cdll.LoadLibrary('/home/user/Tools_App/data_process_demo-main/Sequential_unpacked/libSequentialUnpacker.so')
    lib = ctypes.windll.LoadLibrary('./libSequentialUnpacker.dll')  # use this if run on Win64
    in_filepath_c_str = ctypes.c_char_p(bytes(in_filepath, 'utf-8'))
    out_filepath_c_str = ctypes.c_char_p(bytes(out_filepath, 'utf-8'))
    lib.sequentialUnpacker(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth, in_filepath_c_str, out_filepath_c_str)

# # code below is used for preprocessing a scene (parallel by scenes)
# if __name__ == '__main__':
#     files = sorted(glob.glob('*.raw'))
#     for file in files:
#         # rawPreprocess(3072, 4096, 7168, 14, 14, file, 'unpacked__' + file)
#         rawPreprocess(4912, 8192, 10240, 10, 10, file, 'unpacked__' + file)


if __name__ == '__main__':

    height = 4912
    width = 8192  # 12bit --> 10bit
    stride = 10240
    in_pack_bit_depth = 10
    out_unpack_bit_depth = 10


    ROOT = '.\\data_raw\\'  # 输入根目录改为 received
    OUTPUT_TAG = 'unpack_raw'  # 输出子文件夹名称
    
    # 获取 LensShading_* 文件夹列表
    scenes = glob.glob(os.path.join(ROOT, 'camera_*'))
    
    # 创建输出根目录
    output_root = os.path.join(ROOT, OUTPUT_TAG)
    os.makedirs(output_root, exist_ok=True)
    
    for scene in sorted(scenes):
        scene_name = os.path.basename(scene)
        # 为每个场景创建输出子目录
        output_scene_dir = os.path.join(output_root, scene_name)
        os.makedirs(output_scene_dir, exist_ok=True)
        
        # 查找当前场景下的所有 .raw 文件
        file_paths = sorted(glob.glob(os.path.join(scene, '*.raw')))
        
        for file_path in file_paths:
            # 输出文件名：原文件名 + __unpacked.raw
            out_filename = os.path.basename(file_path).replace('.raw', '__unpacked.raw')
            out_path = os.path.join(output_scene_dir, out_filename)
            
            # print(f"Processing: {file_path} -> {out_path}")
            
            rawPreprocess(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth,
                        file_path, out_path)
