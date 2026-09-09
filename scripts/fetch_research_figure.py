"""Download the owner's published domain map and create a local WebP.

Uses the GitHub contents API because raw.githubusercontent.com is not available
in all environments. No hotlinked image requests are needed by site visitors.
"""
import base64
import io
import json
from pathlib import Path
import urllib.request
from PIL import Image

url = "https://api.github.com/repos/homelessamy/zameen/contents/figures/region_domains.png"
request = urllib.request.Request(url, headers={"User-Agent": "portfolio-figure-import"})
with urllib.request.urlopen(request, timeout=30) as response:
    data = json.load(response)
source = Image.open(io.BytesIO(base64.b64decode(data["content"])))
source.thumbnail((1600, 1600))
target = Path(__file__).resolve().parents[1] / "assets/research/zameen-domains.webp"
source.convert("RGB").save(target, quality=90)
print("Domain map:", source.size, target.stat().st_size, "bytes; source blob", data["sha"])
