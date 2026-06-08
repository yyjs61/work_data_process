import os
import cv2
import numpy as np
import glob

# ================= 配置参数 =================
W = 3840
H = 2176
BP = 1024          # Black Level / 黑电平
WP = 14383         # White Level / 白电平
GAMMA = 2.2        # Gamma 校正系数

# 拜耳阵列格式 (请根据实际 Sensor 调整)
# 常见选项: cv2.COLOR_BAYER_BG2BGR, cv2.COLOR_BAYER_RG2BGR, 
#          cv2.COLOR_BAYER_GR2BGR, cv2.COLOR_BAYER_GB2BGR
BAYER_PATTERN = cv2.COLOR_BAYER_BG2BGR

INPUT_DIR = r"D:\Work\Code\raw_fbd-main\output"
OUTPUT_DIR = r"D:\Work\Code\raw_fbd-main\jpg"
# ==========================================

def process_raw_to_jpg():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 获取所有匹配的 raw 文件并自然排序
    raw_files = sorted(glob.glob(os.path.join(INPUT_DIR, 'req*.raw')))
    
    if not raw_files:
        print("⚠️ 未找到匹配的 req*.raw 文件，请检查 INPUT_DIR 路径！")
        return

    print(f"📦 共找到 {len(raw_files)} 个 Raw 文件，开始处理...")
    
    for idx, file_path in enumerate(raw_files):
        # 1. 读取 Raw 数据 (使用 float32 提升 ISP 管线计算效率与精度)
        img = np.fromfile(file_path, dtype='uint16').reshape([H, W]).astype('float32')
        
        # 2. BP/WP 归一化到 [0, 1]
        img = (img - BP) / (WP - BP)
        img = np.clip(img, 0.0, 1.0)
        
        # 3. Demosaic (OpenCV 要求输入为 uint16 格式)
        img_16 = (img * 65535).astype('uint16')
        img_rgb = cv2.demosaicing(img_16, BAYER_PATTERN).astype('float32') / 65535.0
        
        # 4. 灰度世界白平衡 (Gray World AWB)
        eps = 1e-6
        mean_r = img_rgb[..., 2].mean()
        mean_g = img_rgb[..., 1].mean()
        mean_b = img_rgb[..., 0].mean()
        gray_val = (mean_r + mean_g + mean_b) / 3.0
        
        gain_r = gray_val / (mean_r + eps)
        gain_g = gray_val / (mean_g + eps)
        gain_b = gray_val / (mean_b + eps)
        
        img_rgb[..., 2] *= gain_r
        img_rgb[..., 1] *= gain_g
        img_rgb[..., 0] *= gain_b
        
        # 5. Gamma 校正
        img_rgb = img_rgb ** (1.0 / GAMMA)
        img_rgb = np.clip(img_rgb, 0.0, 1.0)
        
        # 6. 量化为 uint8 并保存 JPG
        out_img = (img_rgb * 255.0).astype('uint8')
        out_name = f"{idx:03d}.jpg"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        
        cv2.imwrite(out_path, out_img)
        print(f"[{idx+1}/{len(raw_files)}] ✅ 已保存: {out_name}")
        
    print("🎉 全部处理完成！")

if __name__ == "__main__":
    process_raw_to_jpg()