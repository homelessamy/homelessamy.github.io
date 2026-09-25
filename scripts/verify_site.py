"""Browser checks for the static portfolio. Requires Playwright and Chromium.

Usage: python scripts/verify_site.py --url http://127.0.0.1:8765
Optional: --axe /path/to/axe.min.js --screenshots /tmp/portfolio-review
"""
import argparse
from html.parser import HTMLParser
import json
import re
from pathlib import Path
import subprocess
from urllib.parse import urlsplit, unquote
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ZAMEEN = "https://github.com/homelessamy/zameen"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--url", default="http://127.0.0.1:8765")
parser.add_argument("--axe", type=Path)
parser.add_argument("--screenshots", type=Path, default=Path("/tmp/portfolio-review"))
args = parser.parse_args()
args.screenshots.mkdir(parents=True, exist_ok=True)


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.ids, self.refs = [], []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        for key in ("href", "src", "data-src", "poster"):
            if key in attrs:
                self.refs.append(attrs[key])


documents = {p: Document(p.read_text()) for p in ROOT.rglob("*.html")}
for path, doc in documents.items():
    assert len(doc.ids) == len(set(doc.ids)), f"Duplicate IDs: {path}"
    for ref in doc.refs:
        parsed = urlsplit(ref)
        if parsed.scheme or parsed.netloc:
            continue
        target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
        assert target.exists(), f"Missing local file: {path}: {ref}"
        if parsed.fragment and target in documents:
            assert unquote(parsed.fragment) in documents[target].ids, f"Missing anchor: {ref}"
print("Local assets, links and anchors: PASS")

home = (ROOT / "index.html").read_text()
kai = (ROOT / "research" / "kai.html").read_text()
for text in ("View still", "View full-size still", "(MP4)", "media-toggle", "jogruber", "research/zameen.html",
             'id="activity"', "drought", "dscourse", "Northeast", "Muhammad-Ahmed-CV.pdf\">CV <span class=\"meta\">"):
    assert text not in home and text not in kai, f"Retired content remains: {text}"
assert home.count("Muhammad-Ahmed-CV.pdf") == 1, "CV should appear only in the shared navigation"
assert not re.search(r"<video[^>]*\scontrols", home), "Videos must not expose controls"
# research/kai.html is a redirect stub: no article, media or navigation.
assert 'name="robots" content="noindex"' in kai and "<video" not in kai and "<nav" not in kai and ".mp4" not in kai
assert "research/kai.html" not in home, "Homepage still links to the retired KAI note"
for fact in ("Approximately 4× fewer parameters", "13.46 million parameters, HEALPix nside 64", "1 January 2018",
             "0.283 K temperature RMSE", "72.4% lower than bicubic on the 2020 test year, averaged across six fitted domains. "
             "On three unseen domains, temperature RMSE is 0.428 K—46.2% lower than bicubic."):
    assert fact in home, f"Research fact changed: {fact}"
assert "8×" not in home and "eight times" not in home, "Retired 8x claim restored"
assert home.count("kai-temperature-bias.mp4") == 1, "Comparison clip must render once"
assert not list(ROOT.rglob("*.pdf")) or [p.name for p in ROOT.rglob("*.pdf")] == ["Muhammad-Ahmed-CV.pdf"], "Unexpected PDF in site output"
try:
    changed = subprocess.run(["git", "status", "--porcelain", "--", "assets/research"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout
    assert not changed.strip(), f"Research assets changed:\n{changed}"
    print("Retired content absent; research assets unchanged: PASS")
except (FileNotFoundError, subprocess.CalledProcessError):
    print("Retired content absent: PASS (git unavailable; research asset check skipped)")

SECTIONS = ["home", "research", "awards", "projects", "experience", "teaching", "education", "skills",
            "about", "beyond-research", "contact"]
# Every enhanced video: autoplaying, muted, looping, no controls, poster matching its still.
ACTIVE = """() => [...document.querySelectorAll('[data-autoplay-media] video')].map(v => {
  const img = v.parentElement.querySelector('img'), frame = img.getBoundingClientRect(), box = v.getBoundingClientRect();
  return {id: v.dataset.src, playing: !v.paused, muted: v.muted, loop: v.loop, autoplay: v.autoplay,
    inline: v.playsInline, controls: v.controls, hidden: v.hidden, src: v.getAttribute('src'),
    poster: v.getAttribute('poster') === img.getAttribute('src'), imgHidden: img.getAttribute('aria-hidden'),
    ratio: Math.abs(frame.width / frame.height / (v.width / v.height) - 1) < 0.01 && Math.abs(box.height - frame.height) < 1.5, preload: v.preload,
    label: !!v.getAttribute('aria-label'), described: !!document.getElementById(v.getAttribute('aria-describedby'))};
})"""
POSTERS = """() => [...document.querySelectorAll('[data-autoplay-media]')].every(f => {
  const v = f.querySelector('video'), img = f.querySelector('img');
  return v.hidden && v.paused && !img.hasAttribute('aria-hidden') && img.getBoundingClientRect().height > 50;
})"""


def check_playing(page, path):
    page.wait_for_function("[...document.querySelectorAll('[data-autoplay-media] video')].every(v => !v.paused && v.currentTime > 0)", timeout=15000)
    for v in page.evaluate(ACTIVE):
        assert v["playing"] and v["muted"] and v["loop"] and v["autoplay"] and v["inline"], (path, v)
        assert not v["controls"] and not v["hidden"] and v["src"] and v["preload"] == "auto", (path, v)
        assert v["poster"] and v["imgHidden"] == "true" and v["ratio"] and v["label"] and v["described"], (path, v)


errors = []
with sync_playwright() as p:
    browser = p.chromium.launch()
    for motion in ("no-preference", "reduce"):
        for theme in ("light", "dark"):
            for width in (1440, 768, 375):
                context = browser.new_context(viewport={"width": width, "height": 1000}, color_scheme=theme, reduced_motion=motion)
                context.route("https://github.com/**", lambda route: route.fulfill(body="GitHub stub"))
                page = context.new_page()
                page.on("pageerror", lambda error: errors.append(str(error)))
                requests = []
                page.on("request", lambda request: requests.append(request.url))
                for path in ("/",):
                    requests.clear()
                    page.goto(args.url + path)
                    page.evaluate("document.fonts.ready")
                    assert page.locator("h1").count() == 1
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"Overflow: {path} {width}"
                    assert page.locator(".theme-toggle").get_attribute("aria-label") == f"Switch to {'dark' if theme == 'light' else 'light'} theme"
                    if motion == "reduce":
                        assert page.evaluate(POSTERS), f"Reduced motion must keep posters: {path}"
                        assert not page.evaluate("[...document.querySelectorAll('video')].some(v => v.getAttribute('src'))")
                        assert not any(url.endswith(".mp4") for url in requests), "Reduced motion loaded video"
                    else:
                        check_playing(page, path)
                        mp4s = {urlsplit(u).path for u in requests if u.endswith(".mp4")}
                        assert not any("europe-wind" in u for u in mp4s), "Orphan Zameen-note video requested"
                        expected = {"water-vapour", "healpix", "kai-temperature-bias", "kai-rollout-10day",
                                    "south-asia-temperature", "cycling"}
                        assert {Path(u).stem for u in mp4s} == expected, mp4s
                    assert not any("jogruber" in url for url in requests), "Contribution API requested"
                    if args.axe and motion == "no-preference":
                        page.add_script_tag(path=str(args.axe))
                        violations = page.evaluate("async () => (await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21aa']}})).violations")
                        assert not violations, json.dumps({"path": path, "width": width, "theme": theme, "violations": [{"id": v["id"], "nodes": [n["target"] for n in v["nodes"]]} for v in violations]}, indent=2)
                    if path == "/":
                        order = page.evaluate("[...document.querySelectorAll('main > section')].map(s => s.id)")
                        assert order == SECTIONS, order
                        assert page.locator("#projects .index-entry").count() == 2
                        assert page.locator("#research article").first.get_attribute("id") == "kai"
                    if motion == "no-preference":
                        page.screenshot(path=str(args.screenshots / f"home-{theme}-{width}.png"), full_page=True)
                context.close()
                print(f"Responsive, theme, media ({motion}): {theme} {width}px PASS")

    # Live preference change: stop and show posters, then restart from the beginning.
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(args.url)
    check_playing(page, "/")
    page.emulate_media(reduced_motion="reduce")
    page.wait_for_function(POSTERS)
    page.emulate_media(reduced_motion="no-preference")
    page.wait_for_function("[...document.querySelectorAll('[data-autoplay-media] video')].every(v => !v.paused && !v.hidden)")
    assert page.evaluate("[...document.querySelectorAll('[data-autoplay-media] video')].every(v => v.currentTime < 2)")
    duration = page.locator("[data-src$='kai-rollout-10day.mp4']").evaluate("v => v.duration")
    assert 3.2 <= duration <= 3.5, f"Not a 10-day clip: {duration}"
    print("Reduced-motion live changes and 10-day clip: PASS")
    context.close()

    # Failed video downloads and browser-blocked autoplay both leave meaningful posters.
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    context.route("**/*.mp4", lambda route: route.abort())
    page = context.new_page()
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(args.url)
    page.wait_for_function(POSTERS)
    context.close()
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    context.add_init_script("HTMLMediaElement.prototype.play = function () { return Promise.reject(new DOMException('Blocked', 'NotAllowedError')); }")
    page = context.new_page()
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(args.url)
    page.wait_for_function(POSTERS)
    context.close()
    print("Failed MP4 and blocked autoplay fall back to posters: PASS")

    context = browser.new_context(viewport={"width": 375, "height": 844})
    page = context.new_page()
    page.goto(args.url)
    page.keyboard.press("Tab")
    assert page.locator(".skip").evaluate("el => el === document.activeElement")
    page.keyboard.press("Enter")
    assert page.locator("#main").evaluate("el => el === document.activeElement")
    page.locator(".menu-toggle").click()
    assert page.locator(".menu-toggle").get_attribute("aria-expanded") == "true"
    page.keyboard.press("Escape")
    assert page.locator(".menu-toggle").get_attribute("aria-expanded") == "false"
    assert page.locator(".menu-toggle").evaluate("el => el === document.activeElement")
    page.locator(".menu-toggle").click()
    page.locator("#primary-nav a[href='#teaching']").click()
    assert page.locator(".menu-toggle").get_attribute("aria-expanded") == "false"
    assert page.locator("#teaching").evaluate("el => el === document.activeElement")
    page.locator(".theme-toggle").click()
    chosen = page.evaluate("document.documentElement.dataset.theme")
    page.reload()
    assert page.evaluate("document.documentElement.dataset.theme") == chosen
    assert page.evaluate("localStorage.getItem('theme')") == chosen
    print("Keyboard, mobile menu, persisted theme: PASS")
    context.close()

    context = browser.new_context(java_script_enabled=False, viewport={"width": 375, "height": 844})
    page = context.new_page()
    page.goto(args.url)
    assert page.locator("#primary-nav").is_visible()
    assert page.locator("#name").is_visible()
    assert page.evaluate("[...document.querySelectorAll('[data-autoplay-media]')].every(f => f.querySelector('video').hidden && f.querySelector('img').getBoundingClientRect().height > 50)")
    assert page.locator("noscript").count() == 0
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    print("No-JavaScript content, navigation and poster fallback: PASS")
    context.close()

    # Retired KAI note: legacy fragments land on fixed homepage anchors; the stub fetches no media.
    legacy = {"": "kai", "#geometry": "kai-geometry", "#comparison-title": "kai-comparison",
              "#rollout-title": "kai-rollout", "#kai-status": "kai", "#anything": "kai"}
    for js in (True, False):
        for fragment, anchor in legacy.items():
            if not js and fragment:
                continue
            context = browser.new_context(java_script_enabled=js)
            page = context.new_page()
            stub_requests = []
            page.on("request", lambda request: stub_requests.append(request.url))
            page.goto(args.url + "/research/kai.html" + fragment, wait_until="commit")
            page.wait_for_url(f"{args.url}/#{anchor}", timeout=5000)
            assert page.locator(f"#{anchor}").count() == 1, anchor
            assert not any("research/" in u and u.endswith(".mp4") for u in stub_requests[:3])
            context.close()
    print("KAI redirect stub and legacy fragments: PASS")

    for js in (True, False):
        context = browser.new_context(java_script_enabled=js)
        context.route("https://github.com/**", lambda route: route.fulfill(body="GitHub stub"))
        page = context.new_page()
        page.goto(args.url + "/research/zameen.html")
        page.wait_for_url(ZAMEEN, timeout=5000)
        context.close()
    print("Zameen redirect stub reaches GitHub (with and without JavaScript): PASS")
    browser.close()
assert not errors, errors
print("Browser console: PASS")
print("Screenshots:", args.screenshots)
