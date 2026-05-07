#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIF 生成脚本 - 修复版
功能：遍历 ./data_raw_bayer/jpg/ 下每个子文件夹，将其中的 .jpg 按自然排序合并为 GIF
支持：文件名含 []() 等特殊字符、绝对路径、详细错误日志
"""

import os
import re
import subprocess
import glob
from pathlib import Path

# ========== 配置区域 ==========
# ROOT = "./data_raw_quad"
    # 定义根目录（请根据实际路径修改）
ROOT = r'C:\Users\admin.DESKTOP-QNCO006\Desktop\IAC4\IAC4_EVT2p3_QUAD_Wide_20260420'

JPG_ROOT = Path(ROOT) / "jpg"
GIF_ROOT = Path(ROOT) / "gif"
FPS = 10
SCALE_WIDTH = 768
DEBUG = True  # 设为 True 可输出详细调试信息
# ============================

def natural_sort_key(text):
    """自然排序：img2 < img10"""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', Path(text).stem)]

def escape_ffmpeg_concat_path(path_str):
    """
    转义 ffmpeg concat demuxer 特殊字符
    参考：https://ffmpeg.org/ffmpeg-formats.html#concat
    """
    # 单引号 -> 两个单引号（ffmpeg concat 语法）
    escaped = path_str.replace("'", "''")
    # 方括号等字符在 concat 中通常安全，但为保险可加引号包裹
    return escaped

def main():
    GIF_ROOT.mkdir(parents=True, exist_ok=True)
    
    if not JPG_ROOT.exists():
        print(f"❌ 错误: 目录不存在: {JPG_ROOT.resolve()}")
        return

    print(f"📁 扫描: {JPG_ROOT.resolve()}\n")

    for group in sorted(os.listdir(JPG_ROOT)):
        group_path = JPG_ROOT / group
        if not group_path.is_dir():
            continue
        
        print(f"🔄 处理: {group}")
        
        # 获取并过滤 .jpg 文件
        jpgs = [p for p in group_path.glob("*.jpg") if not p.name.startswith('.')]
        if not jpgs:
            print(f"   ⚠️  跳过: 无 .jpg 文件\n")
            continue
        
        # 自然排序
        jpgs.sort(key=lambda x: natural_sort_key(x.name))
        print(f"   📸 {len(jpgs)} 张图片")

        # 生成临时文件路径
        frames_txt = group_path / "frames.txt"
        palette_png = group_path / "palette.png"
        gif_path = GIF_ROOT / f"{group}.gif"

        # 写入 frames.txt（关键修复：绝对路径 + 转义 + 正斜杠）
        with open(frames_txt, "w", encoding="utf-8") as f:
            for jpg in jpgs:
                abs_path = jpg.resolve().as_posix()  # 绝对路径 + 正斜杠
                safe_path = escape_ffmpeg_concat_path(abs_path)
                f.write(f"file '{safe_path}'\n")
        
        # 🔍 调试：打印 frames.txt 前 2 行
        if DEBUG:
            with open(frames_txt, "r", encoding="utf-8") as f:
                sample = f.readlines()[:2]
                print(f"   📄 frames.txt 示例:")
                for line in sample:
                    print(f"      {line.strip()}")

        try:
            # 步骤 1: 生成调色板
            print(f"   🎨 生成调色板...")
            cmd1 = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(frames_txt.resolve()),  # 绝对路径
                "-vf", f"fps={FPS},scale={SCALE_WIDTH}:-1:flags=lanczos,palettegen=stats_mode=diff",
                str(palette_png)
            ]
            if DEBUG:
                print(f"   🔧 CMD1: {' '.join(cmd1)}")
            
            result1 = subprocess.run(cmd1, capture_output=True, text=True, check=True)

            # 步骤 2: 生成 GIF
            print(f"   🎬 生成 GIF...")
            cmd2 = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(frames_txt.resolve()),
                "-i", str(palette_png),
                "-filter_complex", f"fps={FPS},scale={SCALE_WIDTH}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=sierra2_4a",
                "-loop", "0",
                str(gif_path)
            ]
            result2 = subprocess.run(cmd2, capture_output=True, text=True, check=True)

            print(f"   ✅ 成功: {gif_path.name}\n")

        except subprocess.CalledProcessError as e:
            print(f"   ❌ FFmpeg 失败 (exit {e.returncode})")
            # 打印关键错误行
            stderr = e.stderr or ""
            for line in stderr.split('\n'):
                if any(kw in line.lower() for kw in ['error', 'impossible', 'no such', 'failed']):
                    print(f"      ⚠️  {line.strip()}")
            # 建议手动测试命令
            print(f"\n   🔍 手动测试建议:")
            print(f"      cd /d {group_path}")
            print(f"      ffmpeg -f concat -safe 0 -i frames.txt -t 1 -f null -\n")
        except Exception as e:
            print(f"   ❌ 未知错误: {type(e).__name__}: {e}\n")
        finally:
            # 清理
            for tmp in [frames_txt, palette_png]:
                if tmp.exists():
                    tmp.unlink()

if __name__ == "__main__":
    print("🚀 GIF 生成脚本启动 (Ctrl+C 中断)\n")
    main()
    print("🎉 完成！")