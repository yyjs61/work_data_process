import os
from glob import glob

ROOT = "/data/0415_hnr_wide_ov52a_dcg_texture_testdata2"

RECEIVED_ROOT = os.path.join(ROOT, "received")
UNPACK_RAW_ROOT = os.path.join(ROOT, "unpack_raw")
YAML_OUT_ROOT = os.path.join(ROOT, "yamls_eachFrame")

os.makedirs(YAML_OUT_ROOT, exist_ok=True)

EXAMPLE_META = """\
Black_level: 1024.0
White_level: 16383.0
height: 2256.0
width: 4000.0
ccm_matrix: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
bayer_pattern: BGGR

isp_gain: 1.0
"""

def load_yaml_text(path):
    with open(path, "r") as f:
        return f.read().strip()

def write_yaml(path, original):
    with open(path, "w") as f:
        f.write(EXAMPLE_META)
        f.write(original)
        f.write("\n")

def process_original_yaml(original_text):
    lines = original_text.splitlines()
    new_lines = []

    for line in lines:
        stripped = line.strip()

        # ❶ 丢弃原始 bayer_pattern（防止重复）
        if stripped.startswith("bayer_pattern:"):
            continue
    
        # ❷ lux -> lux_index / luxid
        if stripped.startswith("lux:"):
            value = stripped.split(":", 1)[1].strip()
            new_lines.append(f"lux_index: {value}")
            new_lines.append(f"luxid: {value}")
            continue

        # ❸ gain -> sensorgain
        if stripped.startswith("gain:"):
            value = stripped.split(":", 1)[1].strip()
            new_lines.append(line)
            new_lines.append(f"sensorgain: {value}")
            continue

        # ❹ 其余原样保留
        new_lines.append(line)

    # ❺ 追加固定 SensorDGain
    new_lines.append("SensorDGain: 1.0")

    return "\n".join(new_lines)




scenes = sorted([d for d in os.listdir(RECEIVED_ROOT)
                 if os.path.isdir(os.path.join(RECEIVED_ROOT, d))])

for idx, scene in enumerate(scenes):
    scene_dir = os.path.join(RECEIVED_ROOT, scene)

    unpack_scene_name = f"{idx:02d}__{scene}"
    unpack_scene_dir = os.path.join(UNPACK_RAW_ROOT, unpack_scene_name)

    if not os.path.isdir(unpack_scene_dir):
        print(f"[SKIP] no unpack_raw for scene: {scene} -> {unpack_scene_name}")
        continue

    yaml_files = glob(os.path.join(scene_dir, "*.yaml"))
    if not yaml_files:
        print(f"[SKIP] no yaml in received scene: {scene}")
        continue

    original_yaml_raw = load_yaml_text(yaml_files[0])
    original_yaml = process_original_yaml(original_yaml_raw)


    raw_files = sorted(glob(os.path.join(unpack_scene_dir, "*.raw")))
    if not raw_files:
        print(f"[SKIP] no raw in unpack_raw scene: {unpack_scene_name}")
        continue

    out_scene_dir = os.path.join(YAML_OUT_ROOT, unpack_scene_name)
    os.makedirs(out_scene_dir, exist_ok=True)

    for i, raw in enumerate(raw_files):
        yaml_name = f"{i:03d}.yaml"
        out_yaml = os.path.join(out_scene_dir, yaml_name)
        write_yaml(out_yaml, original_yaml)

    print(f"[OK] {scene} -> {unpack_scene_name}: {len(raw_files)} yamls generated")
