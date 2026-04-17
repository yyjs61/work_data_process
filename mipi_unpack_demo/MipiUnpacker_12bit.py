import ctypes
import glob
import os

lib = ctypes.cdll.LoadLibrary('/home/user/code/data_process_demo/mipi_unpack_demo/libMipiUnpacker.so')

def rawPreprocess(height, width, stride,
                  in_pack_bit_depth, out_unpack_bit_depth,
                  in_filepath, out_filepath):

    in_filepath_c_str = ctypes.c_char_p(in_filepath.encode('utf-8'))
    out_filepath_c_str = ctypes.c_char_p(out_filepath.encode('utf-8'))

    lib.mipiUnpacker(height,
                     width,
                     stride,
                     in_pack_bit_depth,
                     out_unpack_bit_depth,
                     in_filepath_c_str,
                     out_filepath_c_str)


if __name__ == '__main__':

    height = 2160
    width = 3840
    stride = 5760
    in_pack_bit_depth = 12
    out_unpack_bit_depth = 12

    ROOT = '/data/0318/'
    SRC_ROOT = os.path.join(ROOT, 'received')
    DST_ROOT = os.path.join(ROOT, 'unpack_raw')

    os.makedirs(DST_ROOT, exist_ok=True)

    for root, _, files in os.walk(SRC_ROOT):
        for file in files:
            if not file.lower().endswith('.raw'):
                continue
            in_path = os.path.join(root, file)

            # 保留原有目录结构
            rel_path = os.path.relpath(root, SRC_ROOT)
            out_dir = os.path.join(DST_ROOT, rel_path)
            os.makedirs(out_dir, exist_ok=True)

            out_path = os.path.join(out_dir, file)

            print(f'处理: {in_path}')
            rawPreprocess(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth, in_path, out_path)

    print("全部处理完成")