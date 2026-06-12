import subprocess
from pathlib import Path

# 1. 使用原始字符串(r)避免 Windows 路径中的反斜杠被转义
ROOT = Path(r"D:\Data\20260417\ace_pro2\mp4")
# BASE_PATH = r"D:\Data\20260417\ace_pro2"

# 2. 正确展开通配符，获取该目录下所有 .mp4 文件
# 仅当前目录：*.mp4 | 包含所有子目录递归查找：**.mp4
videos_list = list(ROOT.glob("*.mp4"))

for video in videos_list:
    # 3. 强烈建议将命令参数拆分为列表传入，避免路径中的空格/特殊字符导致解析错误
    command = [r"./ExtraInfoTools/ExtraInfoTools.exe", "-i", str(video), "-a"]
    
    print(f"正在处理: {video.name}")
    # check=True 会在工具执行失败（返回非零退出码）时主动抛出异常，方便排查
    subprocess.run(command, check=True)