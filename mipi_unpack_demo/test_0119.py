import ctypes
import glob
import os
import re

if __name__ == '__main__':

    # ===== RAW 参数 =====
    height = 3072
    width = 4096
    stride = 5120              # RAW10 packed stride
    in_pack_bit_depth = 10
    out_unpack_bit_depth = 10

    # ===== 路径 =====
    ROOT = '/data/CMY_20260119/'
    RECEIVED = os.path.join(ROOT, 'received')
    OUT_DIR = os.path.join(ROOT, 'unpack_raw')
    os.makedirs(OUT_DIR, exist_ok=True)

    # ===== 加载 MIPI unpack 库 =====
    lib = ctypes.cdll.LoadLibrary(
        '/home/user/code/data_process_demo/mipi_unpack_demo/libMipiUnpacker.so'
    )

    # ===== 遍历 RAWMIPI10 文件 =====
    raw_files = sorted(glob.glob(os.path.join(RECEIVED, '*.RAWMIPI10')))
    print(f'找到 {len(raw_files)} 个 RAWMIPI10 文件')

    for raw_path in raw_files:

        if os.path.getsize(raw_path) == 0:
            print(f'{raw_path} 大小为 0，跳过')
            continue

        basename = os.path.basename(raw_path)

        # ===== 从文件名解析 req =====
        m = re.search(r'req\[(\d+)\]', basename)
        if m:
            req_val = int(m.group(1))
            prefix = f'{req_val:03d}__'
        else:
            prefix = '000__'   # 兜底

        # ===== 输出文件名 =====
        out_name = prefix + basename.replace('.RAWMIPI10', '.raw')
        out_path = os.path.join(OUT_DIR, out_name)

        # ===== ctypes 参数 =====
        in_filepath_c = ctypes.c_char_p(raw_path.encode('utf-8'))
        out_filepath_c = ctypes.c_char_p(out_path.encode('utf-8'))

        # ===== unpack =====
        lib.mipiUnpacker(
            height,
            width,
            stride,
            in_pack_bit_depth,
            out_unpack_bit_depth,
            in_filepath_c,
            out_filepath_c
        )

        # ===== size 校验（强烈建议）=====
        expected_size = height * width * 2
        actual_size = os.path.getsize(out_path)
        if actual_size != expected_size:
            print(
                f'[WARN] size mismatch: {out_name} '
                f'exp={expected_size}, got={actual_size}'
            )
