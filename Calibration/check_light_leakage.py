import numpy as np
import matplotlib.pyplot as plt
import os
import glob
from scipy.ndimage import gaussian_filter

# ================= 配置区域 =================
# 请修改为你存放 100+ 张黑图的路径
DATA_DIR = r"D:\etc\IAC4\data\data_IAC4\BlackLevel\sdcard_gain64_3"

# 图像基本参数 (请根据实际 Sensor 规格确认)
IMG_WIDTH = 4096   # 例如: 3840, 4096, 5472 等
IMG_HEIGHT = 3600  # 例如: 2176, 3072, 3600 等
BLACK_LEVEL = 64   # 黑电平 (BLK)，常见值: 64, 1024, 4096 等
ISO_VALUE = 6400    # 仅用于文件名标记

# 平滑系数 (Sigma)，越大越平滑，越能看出大趋势，但会丢失细节
GAUSSIAN_SIGMA = 5.0 

# 匹配模式，确保只读取黑图
RAW_PATTERN = "*.raw" 
# ===========================================

def process_average_leakage(data_dir, width, height, black_level, iso, sigma=5.0):
    """
    读取目录下所有 raw 文件，计算平均黑图，并可视化漏光趋势
    """
    raw_files = sorted(glob.glob(os.path.join(data_dir, RAW_PATTERN)))
    
    if not raw_files:
        print(f"[ERROR] 在路径 {data_dir} 下未找到匹配 '{RAW_PATTERN}' 的文件！")
        return

    total_frames = len(raw_files)
    print(f"[INFO] 找到 {total_frames} 个 Raw 文件，开始累加平均...")
    
    # 使用 float64 进行累加，防止 uint16 溢出并保留精度
    accumulator = np.zeros((height, width), dtype=np.float64)
    
    for i, f_path in enumerate(raw_files):
        try:
            # 读取数据
            data = np.fromfile(f_path, dtype=np.uint16)
            if data.size != width * height:
                print(f"  [SKIP] {os.path.basename(f_path)}: 尺寸不匹配 (期望 {width*height}, 实际 {data.size})")
                continue
            
            #  reshape 并转为 float64 累加
            img = data.reshape((height, width)).astype(np.float64)
            accumulator += img
            
            # 每处理 10 张打印一次进度
            if (i + 1) % 10 == 0 or (i + 1) == total_frames:
                print(f"  Progress: {i+1}/{total_frames}")
                
        except Exception as e:
            print(f"  [ERROR] 处理 {os.path.basename(f_path)} 时出错: {e}")
            continue

    if total_frames == 0:
        print("[ERROR] 没有成功读取任何文件。")
        return

    # 1. 计算平均值
    avg_raw = accumulator / total_frames
    print(f"[INFO] 平均完成。全局均值 (Raw): {np.mean(avg_raw):.2f}")

    # 2. 黑电平校正 (BLC)
    avg_blc = avg_raw - black_level
    
    # 3. 计算残差 (相对于全局均值)
    global_mean = np.mean(avg_blc)
    residual = avg_blc - global_mean
    
    print(f"[INFO] BLC 后全局均值: {global_mean:.2f}, Std: {np.std(residual):.2f}")

    # 4. 高斯平滑 (去除随机噪声，突出漏光/Shading 趋势)
    residual_smoothed = gaussian_filter(residual, sigma=sigma)
    
    # 5. 确定显示范围 (Colorbar Range)
    # 对于平均后的图，噪声极小，残差通常很小。
    # 我们使用 3倍标准差来覆盖绝大多数像素，避免个别坏点拉伸动态范围
    res_std = np.std(residual_smoothed)
    clip_val = max(res_std * 3.0, 1.0) 
    
    print(f"[INFO] 可视化范围设定为: +/- {clip_val:.2f} DN")

    # 6. 可视化绘图
    fig, ax = plt.subplots(figsize=(12, 10), dpi=150)
    
    # 使用 'viridis' 或 'seismic' (蓝-白-红) 
    # seismic 更适合看正负偏差，viridis 更适合看强度分布
    im = ax.imshow(residual_smoothed, cmap='viridis', 
                   vmin=-clip_val, vmax=clip_val,
                   aspect='auto')
    
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('DN Deviation from Mean', rotation=270, labelpad=20)
    
    title_str = (f'Average Light Leakage Trend ({total_frames} frames averaged)\n'
                 f'Mean BL: {global_mean:.2f} | Sigma: {sigma} | Range: +/- {clip_val:.1f} DN')
    ax.set_title(title_str, fontsize=12, pad=15)
    
    ax.set_xticks([])
    ax.set_yticks([])
    
    # 7. 保存结果
    output_name = f"avg_leakage_{total_frames}frames_iso{iso}.jpg"
    output_path = os.path.join(data_dir, output_name)
    
    try:
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"[SUCCESS] 图片已保存至: {output_path}")
    except Exception as e:
        print(f"[ERROR] 保存失败: {e}")
    finally:
        plt.close(fig)

if __name__ == "__main__":
    # 执行主逻辑
    process_average_leakage(
        data_dir=DATA_DIR,
        width=IMG_WIDTH,
        height=IMG_HEIGHT,
        black_level=BLACK_LEVEL,
        iso=ISO_VALUE,
        sigma=GAUSSIAN_SIGMA
    )