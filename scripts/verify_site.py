"""Browser checks for the static portfolio. Requires Playwright and Chromium.

Usage: python scripts/verify_site.py --url http://127.0.0.1:8765
Optional: --axe /path/to/axe.min.js --screenshots /tmp/portfolio-review
"""
import argparse
from datetime import date, timedelta
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlsplit, unquote
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
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
        for key in ("href", "src", "data-src"):
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

today = date.today()
days = [{"date": str(today - timedelta(days=364-i)), "count": i % 5, "level": i % 5} for i in range(365)]
fixture = {"contributions": days}
errors = []
with sync_playwright() as p:
    browser = p.chromium.launch()
    for theme in ("light", "dark"):
        for width in (1440, 768, 390, 320):
            context = browser.new_context(viewport={"width": width, "height": 1000}, color_scheme=theme, reduced_motion="reduce")
            context.route("**/github-contributions-api.jogruber.de/**", lambda route: route.fulfill(json=fixture))
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            requests = []
            page.on("request", lambda request: requests.append(request.url))
            for path in ("/", "/research/zameen.html", "/research/kai.html"):
                page.goto(args.url + path)
                page.evaluate("document.fonts.ready")
                assert page.locator("h1").count() == 1
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"Overflow: {path} {width}"
                assert not page.evaluate("[...document.querySelectorAll('video')].some(v => !v.paused || v.getAttribute('src'))"), "Media loaded without play"
                assert not any(url.endswith(".mp4") for url in requests), "Unrequested video download"
                assert page.locator(".theme-toggle").get_attribute("aria-label") == f"Switch to {'dark' if theme == 'light' else 'light'} theme"
                if args.axe:
                    page.add_script_tag(path=str(args.axe))
                    violations = page.evaluate("async () => (await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21aa']}})).violations")
                    assert not violations, json.dumps({"path":path,"width":width,"theme":theme,"violations":[{"id":v["id"],"nodes":[n["target"] for n in v["nodes"]]} for v in violations]}, indent=2)
                slug = "home" if path == "/" else Path(path).stem
                if width in (1440,390):
                    page.screenshot(path=str(args.screenshots / f"{slug}-{theme}-{width}.png"), full_page=True)
                if path == "/":
                    assert page.locator("#research article").first.get_attribute("id") == "kai"
                    page.locator("#activity").scroll_into_view_if_needed()
                    page.wait_for_selector("#heatmap-scroll:not([hidden])")
                    assert page.locator("#heatmap i[data-level]").count() == 365
                    if width == 1440:
                        page.screenshot(path=str(args.screenshots / f"activity-{theme}.png"))
            context.close()
            print(f"Responsive, theme, media, accessibility: {theme} {width}px PASS")

    context = browser.new_context(viewport={"width":390,"height":844})
    context.route("**/github-contributions-api.jogruber.de/**", lambda route: route.abort())
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
    page.locator("#activity").scroll_into_view_if_needed()
    assert page.locator("#activity-fallback").is_visible()
    print("Keyboard, mobile menu, persisted theme, API failure: PASS")
    page.goto(args.url + "/research/kai.html")
    button = page.locator("button[aria-controls='rollout-video']")
    button.click()
    page.wait_for_function("!document.getElementById('rollout-video').paused")
    duration = page.locator("#rollout-video").evaluate("v => v.duration")
    assert 3.2 <= duration <= 3.5, f"Not a 10-day clip: {duration}"
    button.click()
    assert page.locator("#rollout-video").evaluate("v => v.paused")
    button.click()
    page.wait_for_function("!document.getElementById('rollout-video').paused")
    page.emulate_media(reduced_motion="reduce")
    page.wait_for_function("document.getElementById('rollout-video').hidden")
    assert page.locator("#rollout-video").evaluate("v => v.paused")
    print("10-day video playback, pause, reduced-motion change: PASS")
    context.close()
    context = browser.new_context(java_script_enabled=False, viewport={"width":390,"height":844})
    page = context.new_page()
    page.goto(args.url)
    assert page.locator("#primary-nav").is_visible()
    assert page.locator("#name").is_visible()
    assert page.locator("noscript a").first.is_visible()
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    print("No-JavaScript content, navigation and media fallback: PASS")
    context.close()
    browser.close()
assert not errors, errors
print("Browser console: PASS")
print("Screenshots:", args.screenshots)
