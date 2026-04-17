import ctypes
import glob
import os

lib = ctypes.cdll.LoadLibrary('/home/user/code/data_process_demo/mipi_unpack_demo/libMipiUnpacker_support_mipi14.so')

lib.mipiUnpacker.argtypes = [
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_char_p,
    ctypes.c_char_p
]

lib.mipiUnpacker.restype = ctypes.c_int

def rawPreprocess(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth, in_filepath, out_filepath):

    in_filepath_c_str = ctypes.c_char_p(in_filepath.encode('utf-8'))
    out_filepath_c_str = ctypes.c_char_p(out_filepath.encode('utf-8'))

    lib.mipiUnpacker(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth, in_filepath_c_str, out_filepath_c_str)

if __name__ == '__main__':

    height = 2304
    width = 4096
    stride = 7168
    in_pack_bit_depth = 14
    out_unpack_bit_depth = 14

    ROOT = '/data/0324_hnr_cmy_ob_debug/'
    SRC_ROOT = ROOT
    DST_ROOT = os.path.join(ROOT, 'unpack_raw')

    os.makedirs(DST_ROOT, exist_ok=True)

    files = sorted(glob.glob(os.path.join(SRC_ROOT, '*.RAWMIPI14')))

    for file in files:
        filename = os.path.basename(file)
        out_path = os.path.join(DST_ROOT, 'unpacked__' + filename.replace('.RAWMIPI14', '.raw'))

        print(f'处理: {file}')

        rawPreprocess(height, width, stride, in_pack_bit_depth, out_unpack_bit_depth, file, out_path)

    print("全部处理完成")