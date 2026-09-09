"""Optimize scientific exports. Usage: python scripts/prepare_media.py ORIGINALS.

Requires FFmpeg on PATH or imageio-ffmpeg. Originals are never modified.
"""
import argparse
from pathlib import Path
import shutil
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("originals", type=Path)
args = parser.parse_args()
ffmpeg = shutil.which("ffmpeg")
if not ffmpeg:
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
output = Path(__file__).resolve().parents[1] / "assets" / "research"
output.mkdir(parents=True, exist_ok=True)
exports = {
    "water-vapour": ("viz_globe_tcwv.mp4", 660),
    "south-asia-temperature": ("lens_SASIA_t2m.gif", 704),
    "europe-wind": ("lens_EURO_wind.gif", 704),
    "kai-temperature-bias": ("fig_multimodel_bias_t2m.gif", 1350),
    "kai-rollout-10day": ("fig_rollout40_localnorm.gif", 1426),
    "healpix": ("viz_healpix_geometry.mp4", 1140),
}
for name, (original, width) in exports.items():
    base = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(args.originals / original)]
    filters = f"scale={width}:trunc(ih/2)*2"
    timing = []
    # Original: 40 daily frames at 330 ms each. Publish the first ten days'
    # map panels only; remove the 40-day title and curves, not scientific data.
    if name == "kai-rollout-10day":
        filters = "crop=1426:324:0:36"
        timing = ["-t", "3.3"]
    subprocess.run(base + ["-vf", filters, "-frames:v", "1", "-c:v", "libwebp", "-quality", "88",
                          str(output / f"{name}.webp")], check=True)
    subprocess.run(base + timing + ["-vf", filters, "-an", "-c:v", "libx264", "-crf", "22",
                          "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                          str(output / f"{name}.mp4")], check=True)
    print(name, (output / f"{name}.mp4").stat().st_size, "bytes")
