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

- `index.html`: the one-page narrative. Section order: Hero → Selected Research
  (**KAI-α**, **Zameen**) → Awards → Other Work → Experience → Teaching →
  Education → Research & Technical Toolkit → About → Beyond Research → Contact.
  Awards and Beyond Research are intentionally not in the navigation. The CV is
  linked only from the shared navigation; the GitHub profile only from Contact.
- `research/kai.html`: KAI research note, HEALPix geometry, **days 1–10 only** of
  the autoregressive rollout, and comparative temperature bias.
- `research/zameen.html`: not a research page. A `noindex` redirect stub
  (`location.replace` plus a zero-second meta refresh, canonical to GitHub) that
  sends old inbound links to https://github.com/homelessamy/zameen. Nothing on the
  site links to it. The homepage Zameen entry links straight to the repository.
- `styles.css`: shared Archivo / Source Serif 4 / Plex Mono typography, warm
  neutral and scientific teal themes, a 1120px canvas, responsive layouts.
- `theme.js`: early restoration of the existing `theme` localStorage key.
- `site.js`: progressive enhancement for navigation, theme, and autoplaying
  media. Content remains static HTML. There is no GitHub activity section and no
  third-party API request.

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

The award (First Prize, Disaster Safety category, 2026 KMA Weather Big Data
Contest; Asian Union, team lead) is sourced from the owner's competition deck and
the [KMA announcement](https://www.kma.go.kr/kma/news/press_01.jsp?bid=press&from=2026-05-09&mode=view&num=1194712&page=1&to=2026-08-09)
of 6 August 2026. `assets/awards/kma-asian-union-cover.webp` (1600 × 900) is
rendered from **page 1 only** of the deck, uncropped and unedited. The full PDF is
deliberately kept outside the repository and must not be committed or linked.

## Media

Research videos are local H.264 MP4 with fast-start metadata, no audio, and
explicit dimensions; each has a static WebP poster. At the owner's request every
animation **autoplays from first load**, muted, inline and looping, with **no
controls** of any kind (no play/pause button, hover pause, offscreen or
tab-visibility pause, or single-player rule). Clips start at time zero and loop
independently.

- The `<video>` carries `autoplay loop muted playsinline preload="auto"`, the
  mapped `poster`, intrinsic `width`/`height`, `aria-label` and
  `aria-describedby`. Its MP4 URL sits in `data-src`; `site.js` checks
  `prefers-reduced-motion` and, for ordinary motion, assigns every source on DOM
  ready and calls `play()`, handling rejection.
- The poster `<img>` stays in flow underneath to reserve the aspect ratio. It is
  `aria-hidden` only while its video is active, so there is one announcement.
- Reduced motion: no MP4 is requested and posters stay. Switching to reduce stops
  playback and restores the poster; switching back restarts from the beginning.
- No JavaScript, failed download, or browser-blocked autoplay: the poster image,
  its alt text and caption remain. There are no MP4 or “View still” links.
- Print shows posters. `europe-wind` and `zameen-domains` are retained in
  `assets/research/` but have no placement since the Zameen note was retired.

**Known accessibility limitation.** Continuous looping motion longer than five
seconds with no pause mechanism does not meet WCAG 2.2.2 (Pause, Stop, Hide) for
visitors without a reduced-motion preference. This is an owner-accepted exception;
the site does not claim WCAG AA conformance.

Beyond Research uses `assets/activities/cycling.mp4`, the first 14 s of the
owner's clip re-encoded with the owner's approval (540 × 960, H.264 CRF 26, no
audio, metadata stripped, fast-start; ~1.6 MB, down from ~28 MB), and
`assets/activities/cycling.jpg`, the owner's photo shown beside the clip (720 ×
1280, EXIF including GPS location removed, orientation applied, ~1px trimmed from
each side for 9:16). The clip's poster, `cycling-ride.jpg`, is its own frame at 3 s.

Regenerate derived assets from the original exports:

```sh
python scripts/prepare_media.py /path/to/original-exports
```

Requires FFmpeg on PATH or `imageio-ffmpeg`. This is an authoring tool, not a site
dependency. The original GIFs remain untouched and are not included in page loads.
Do not re-run it against the shipped MP4s: they are intentionally not re-encoded.

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
  "project": "research/kai.html"
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
themes. See the WCAG 2.2.2 limitation above.

Browser verification requires Playwright and an installed Chromium. Axe is
optional but recommended. Neither is a site dependency:

```sh
python scripts/verify_site.py --url http://127.0.0.1:8765 --axe /path/to/axe.min.js
```

Checks cover local links/assets/posters/anchors, retired content, unchanged
research assets (via git), section order, 1440/768/375px in both themes, axe
WCAG A/AA rules, autoplay state (muted, looping, inline, no controls, poster,
aspect ratio), reduced motion on load and on live change, failed MP4 and blocked
autoplay fallbacks, keyboard/menu/theme persistence, no-JavaScript posters, and
the Zameen redirect with and without JavaScript. GitHub is stubbed in the browser
checks; check real destinations separately.

Automated accessibility checks do not replace a screen-reader review. Local
performance observations are not field Core Web Vitals measurements.

## Maintenance notes (not reader-facing)

- `Muhammad-Ahmed-CV.pdf` is stale; the owner will replace it under the same
  filename, so no link changes are needed.
- The MetaEarth title is “Master’s Student” (owner-confirmed). The Experience
  entry keeps its May 2024 start and notes the earlier Research Intern role;
  no internship end date is stated.
- KAI's parameter comparison reads “approximately 4× fewer parameters” than
  GraphCast and FourCastNet, per the owner; the separate 13.46M rollout
  configuration figure is unchanged.
