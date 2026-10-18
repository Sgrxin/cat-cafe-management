# -*- coding: utf-8 -*-
"""参考视频抽帧（imageio-ffmpeg 自带 ffmpeg）"""
import subprocess
from pathlib import Path

FF = r"C:\Users\lx\AppData\Local\Programs\Python\Python312\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
video = r"C:\Users\lx\Desktop\agent\agent\毕设\参考视频\Desktop 2026.10.18 - 11.57.30.01.mp4"
out_dir = Path(r"C:\Users\lx\AppData\Local\Temp\opencode\ref_frames")
out_dir.mkdir(parents=True, exist_ok=True)

for i, t in enumerate([3, 8, 15, 22, 30, 38]):
    out = out_dir / f"frame_{i}.png"
    subprocess.run([FF, "-y", "-ss", str(t), "-i", video, "-frames:v", "1",
                    "-vf", "scale=1280:-1", str(out)], capture_output=True)
    ok = out.exists() and out.stat().st_size > 10000
    print(f"frame_{i} @{t}s:", "OK" if ok else "FAIL")
