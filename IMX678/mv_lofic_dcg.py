import os
import shutil
import yaml
from pathlib import Path

class ISPRawProcessor:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.received_path = self.base_path / "received"

    def move_and_rename_raws(self):
        """
        功能：
        1. 遍历 received 下的所有场景文件夹
        2. 将 long_unpack 和 short_unpack 下的 raw 文件移动到场景根目录
        3. 重命名：添加 __long 或 __short 后缀
        """
        if not self.received_path.exists():
            print(f"错误：找不到路径 {self.received_path}")
            return

        print(f"开始处理路径：{self.received_path} ...")
        
        # 遍历 received 下的所有子文件夹（即场景文件夹）
        scene_folders = [f for f in self.received_path.iterdir() if f.is_dir()]
        
        for scene_dir in scene_folders:
            print(f"\n正在处理场景：{scene_dir.name}")
            
            # 处理 Long 帧
            long_dir = scene_dir / "long_unpack"
            if long_dir.exists():
                self._process_subfolder(long_dir, scene_dir, suffix="__long")
            else:
                print(f"  [跳过] 未找到 long_unpack 文件夹")

            # 处理 Short 帧
            short_dir = scene_dir / "short_unpack"
            if short_dir.exists():
                self._process_subfolder(short_dir, scene_dir, suffix="__short")
            else:
                print(f"  [跳过] 未找到 short_unpack 文件夹")

    def _process_subfolder(self, source_dir, target_dir, suffix):
        """
        辅助函数：移动文件并重命名
        """
        raw_files = list(source_dir.glob("*.raw"))
        if not raw_files:
            return
            
        print(f"  -> 发现 {len(raw_files)} 个 raw 文件在 {source_dir.name}，开始移动...")
        
        for raw_file in raw_files:
            # 构建新文件名：原名 + 后缀 + .raw
            # 例如: dump_bayer...00000.raw -> dump_bayer...00000__long.raw
            new_filename = f"{raw_file.stem}{suffix}{raw_file.suffix}"
            target_path = target_dir / new_filename
            
            try:
                shutil.move(str(raw_file), str(target_path))
                # print(f"     [OK] {raw_file.name} -> {new_filename}")
            except FileExistsError:
                print(f"     [警告] 目标文件已存在，跳过：{target_path}")
            except Exception as e:
                print(f"     [错误] 处理文件失败：{e}")

    def generate_yaml_from_meta(self):
        """
        功能：
        遍历场景，如果存在 meta.txt，将其转换为 yaml 文件。
        假设 meta.txt 格式为 key=value 或 key: value
        """
        if not self.received_path.exists():
            return

        print(f"\n开始生成 YAML 配置文件...")
        
        for scene_dir in self.received_path.iterdir():
            if not scene_dir.is_dir():
                continue
                
            meta_file = scene_dir / "meta.txt"
            if meta_file.exists():
                yaml_file = scene_dir / "config.yaml"
                try:
                    config_data = self._parse_meta_file(meta_file)
                    with open(yaml_file, 'w', encoding='utf-8') as f:
                        yaml.dump(config_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                    print(f"  [生成] {scene_dir.name}/config.yaml")
                except Exception as e:
                    print(f"  [错误] 生成 {scene_dir.name} 的 yaml 失败: {e}")
            else:
                # print(f"  [跳过] {scene_dir.name} 下无 meta.txt")
                pass

    def _parse_meta_file(self, file_path):
        """
        解析 meta.txt。
        支持格式：
        gain=16
        exposure=1000
        或者
        gain: 16
        """
        data = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 尝试分割 = 或 :
                separator = '='
                if ':' in line and '=' not in line:
                    separator = ':'
                elif ':' in line and '=' in line:
                    # 优先处理第一个出现的
                    separator = '=' if line.index('=') < line.index(':') else ':'

                if separator in line:
                    key, value = line.split(separator, 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 尝试将数值转换为 int 或 float
                    try:
                        if '.' in value:
                            value = float(value)
                        else:
                            value = int(value)
                    except ValueError:
                        pass # 保持字符串
                    
                    data[key] = value
        return data

if __name__ == "__main__":
    # 配置根目录路径
    # ROOT_DIR = r"D:\Data\2026_05\20\Test_data_260520\IMX678_Test_data_260520"
    ROOT_DIR = r"D:\Data\2026_05\21\IMX678_Test_data_260521"
    
    processor = ISPRawProcessor(ROOT_DIR)
    
    # 1. 执行 Raw 文件移动和重命名
    processor.move_and_rename_raws()
    
    # 2. 执行 Meta 转 YAML (如果需要)
    # processor.generate_yaml_from_meta()
    
    print("\n处理完成！")