# Muhammad Ahmed · research portfolio

A static, research-led personal site for GitHub Pages. No framework, runtime
dependencies, build step, or external font service is needed to serve it.

## Preview

```sh
python -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765`. The existing GitHub Pages repository and deployment
structure are retained. Publishing still happens through the repository's normal
GitHub Pages workflow; the redesign itself does not push or deploy anything.

## Content and layout

- `index.html`: the one-page narrative, led by **KAI-α**, then **Zameen**, followed
  by Other Work, Experience, Teaching, Education, Toolkit, About, GitHub, Contact.
- `research/kai.html`: KAI research note, HEALPix geometry, **days 1–10 only** of
  the autoregressive rollout, and comparative temperature bias.
- `research/zameen.html`: graph downscaling motivation, method, geographic
  evaluation, contextualized results, contributions, and limitations.
- `styles.css`: shared Archivo / Source Serif 4 / Plex Mono typography, warm
  neutral and scientific teal themes, a 1120px canvas, responsive layouts.
- `theme.js`: early restoration of the existing `theme` localStorage key.
- `site.js`: progressive enhancement for navigation, theme, scientific video
  controls, and GitHub contributions. Research content remains static HTML.

PcMAN-DS is intentionally omitted. Teaching information is supplied by the owner:
Intermediate Writing and English Presentation and Discussion (KAIST, Summer
2024); Scientific Writing (KAIST, Fall 2026). Course codes and unconfirmed teaching
responsibilities are not invented. Education and experience are grounded in the
existing CV; the CV PDF itself has not been edited.

Zameen methods and results are based on the owner's
[technical report](https://github.com/homelessamy/zameen/blob/main/README.md),
consulted 9 September 2026 (README blob `0d4483e66cc3cf474d0c152727839c000f1488ea`).
Its 2020 results replace older aggregate claims from the previous portfolio.
KAI's approximate parameter comparison and the author's contributions come from
the existing site/CV; the supplied figures identify their own model variants.
No publication, DOI, acceptance status, or private code link is fabricated.

## Research media

Videos are local, H.264 MP4 with fast-start metadata, no audio, and explicit
dimensions. Every animation has a static WebP poster, descriptive text, and an
explicit play/pause control. Below-fold images load lazily. Video URLs are assigned
only after a user presses Play; nothing autoplays. Only one animation plays at a
time. Videos pause offscreen and when the tab is hidden. Switching to reduced
motion restores posters; a visitor may still explicitly choose to play a clip.
Without JavaScript, figures and direct MP4 links remain available.

Regenerate derived assets from the original exports:

```sh
python scripts/prepare_media.py /path/to/original-exports
```

Requires FFmpeg on PATH or `imageio-ffmpeg`. This is an authoring tool, not a site
dependency. The original GIFs remain untouched and are not included in page loads.

| Web asset | Original | Treatment |
| --- | --- | --- |
| water-vapour | viz_globe_tcwv.mp4 | Optimized globe + poster |
| south-asia-temperature | lens_SASIA_t2m.gif | Zameen temperature comparison |
| europe-wind | lens_EURO_wind.gif | Zameen wind comparison |
| kai-temperature-bias | fig_multimodel_bias_t2m.gif | Full comparison panels |
| kai-rollout-10day | fig_rollout40_localnorm.gif | First ten frames (3.3 s); map panels only |
| healpix | viz_healpix_geometry.mp4 | Globe and unfolded faces |

The ten-day clip omits the original 40-day heading, error curves and time axis;
it preserves the map values, day labels and fixed colour scales. No 40-day video
is shipped. `scripts/fetch_research_figure.py` imports the owner's domain map from
the GitHub contents API and optimizes it locally (Pillow required).

## Publications

`publications.json` starts empty. `scripts/build_publications.py` renders entries
between the publication markers in `index.html`; an empty list emits no section.
Add only verified records using this shape (illustrative placeholders, not a paper):

```json
{
  "authors": ["Author One", "Author Two"],
  "title": "Verified research title",
  "venue": "Venue, if applicable",
  "status": "In preparation",
  "year": 2026,
  "paper": null,
  "code": null,
  "project": "research/zameen.html"
}
```

Supported statuses: `Preprint`, `Under review`, `In preparation`, `Published`.
Optional paper/code/project links appear only when populated. Link values must be
HTTPS URLs or local `research/` paths. Entries retain the order in the JSON list.

```sh
python scripts/build_publications.py
python scripts/build_publications.py --check
```

## Accessibility and verification

The site retains semantic landmarks, a skip link, visible focus rings, sensible
headings, system theme detection and a persistent manual theme switch. Mobile
navigation supports keyboard use and Escape. All navigation is visible without
JavaScript. Scientific images keep their original data colour scales in both
themes. GitHub history is supplementary, loaded near the section, cached for six
hours, and replaced with a useful profile link if its third-party API fails.

Browser verification requires Playwright and an installed Chromium. Axe is
optional but recommended:

```sh
python scripts/verify_site.py --url http://127.0.0.1:8765 --axe /path/to/axe.min.js
```

Checks cover local links/assets/anchors, 320/390/768/1440px widths in both themes,
WCAG A/AA automated rules, keyboard navigation, mobile menu focus, theme persistence,
contribution rendering and API failure, video loading/playback, the ten-day clip,
reduced-motion changes, and no-JavaScript fallbacks. Contribution data is mocked
for deterministic checks; no fabricated activity is included in the shipped site.

Automated accessibility checks do not replace a screen-reader review. Local
performance observations are not field Core Web Vitals measurements.
