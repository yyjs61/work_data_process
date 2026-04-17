import os, glob

def unpack_14bit_raw_le(input_path, output_path):
    if not os.path.exists(input_path):
        print(f'NO SUCH FILE: {input_path}')
        return

    PACK_SIZE = 7
    
    input_size = os.path.getsize(input_path)
    print(f'unpacking (LSB): {input_path} ({input_size} bytes)')

    with open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
        while True:
            chunk = f_in.read(PACK_SIZE)
            if len(chunk) < PACK_SIZE:
                break
            
            val = int.from_bytes(chunk, byteorder='little')

            p1 = val & 0x3FFF
            p2 = (val >> 14) & 0x3FFF
            p3 = (val >> 28) & 0x3FFF
            p4 = (val >> 42) & 0x3FFF

            for pixel in [p1, p2, p3, p4]:
                f_out.write(pixel.to_bytes(2, byteorder='little'))

    print(f'output: {output_path}')


if __name__ == '__main__':
    files = sorted(glob.glob('*.raw'))
    for F in files:
        unpack_14bit_raw_le(F, 'unpacked__' + F)

