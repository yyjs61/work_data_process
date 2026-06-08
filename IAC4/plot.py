import os
import yaml
import glob
import matplotlib.pyplot as plt

# ROOT = "/data/HP3_QuadBayer_20260122_High_Texture_day/yamls_eachFrame"
# ROOT = r'D:\Data\2026_06\01\IAC4_IMX01F_DCG_ER4_Wide_Night_dumpraw_20260601/yamls_eachFrame'
ROOT = r'D:\Data\2026_06\03\IAC4_IMX01F_DCG_ER4_Wide_20260603'

ROOT += r"/yamls_eachFrame"

OUT_DIR = os.path.join(ROOT, "plots")
os.makedirs(OUT_DIR, exist_ok=True)

for scene_name in os.listdir(ROOT):
    scene_path = os.path.join(ROOT, scene_name)
    yaml_files = sorted(glob.glob(os.path.join(ROOT, scene_name, '*.yaml')))

    expotimes = []
    again = []
    frame_numbers = []

    for idx, yf in enumerate(yaml_files):
        yaml_path = yf  # glob 已经是完整路径
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)
        
        expotimes.append(data.get("expotime", 0) / 1000000)  # ns -> ms
        again.append(data.get("SensorAGain", data.get("again", 1)))
        frame_numbers.append(idx + 1)

    fig, ax1 = plt.subplots(figsize=(12, 6))
    color1 = 'tab:blue'
    ax1.set_xlabel("Frame Number")
    ax1.set_ylabel("Exposure Time (ms)", color=color1)
    ax1.plot(frame_numbers, expotimes, color=color1, label="Exposure Time")
    ax1.tick_params(axis='y', labelcolor=color1)


    ax2 = ax1.twinx()  
    color2 = 'tab:red'
    ax2.set_ylabel("Sensor AGain", color=color2)
    ax2.plot(frame_numbers, again, color=color2, label="AGain")
    ax2.tick_params(axis='y', labelcolor=color2)

    plt.title(f"Exposure Info - Scene: {scene_name}")
    fig.tight_layout()

    plot_file = os.path.join(OUT_DIR, f"{scene_name}_exposure.png")
    plt.savefig(plot_file)
    plt.close()
    print(f"Saved plot for scene {scene_name} -> {plot_file}")
