# Research Log · widgets

Small, self-contained HTML instruments for the **Research Log (v2)** Notion workspace.
Each file is one page with inline CSS/JS, a transparent background, and an
edit-me `CONFIG` block at the top of its `<script>`. The only network calls are
Google Fonts (Newsreader + IBM Plex Mono), `api.open-meteo.com` (weather) and
`open.spotify.com` (player).

Design system "Ink & Brass": surface `#232220`, text `#ECE6DA`, muted `#A39D90`,
one brass accent `#D9A658`, hairlines `rgba(236,230,218,.10)`. Add `?theme=paper`
for a light variant (`#F6F3EC` / `#26231F` / brass `#8F6418`) or `?theme=auto`
to follow the OS setting.

Base URL: `https://homelessamy.github.io/research-log/`

| Widget | Embed URL | Suggested size in Notion |
|---|---|---|
| Instrument strip (Home) | https://homelessamy.github.io/research-log/strip.html | full page width × **330 px** (works 280–420) |
| Clock, KST + PKT | https://homelessamy.github.io/research-log/clock.html | 340 × 280, or 560 × 280 (wide) |
| Focus timer | https://homelessamy.github.io/research-log/timer.html | 340 × 340, or 640 × 320 (wide) |
| Spotify · Parhai | https://homelessamy.github.io/research-log/spotify.html | any width × 210 |
| Weather, Daejeon | https://homelessamy.github.io/research-log/weather.html | 340 × 300, or 560 × 320 |
| Countdown | https://homelessamy.github.io/research-log/countdown.html | 340 × 260 |
| Semester / graduation progress | https://homelessamy.github.io/research-log/progress.html | 340 × 300 |
| Quote of the day | https://homelessamy.github.io/research-log/quote.html | 560 × 220 |
| Moon almanac | https://homelessamy.github.io/research-log/moon.html | 340 × 300 |
| GPU-hours ledger | https://homelessamy.github.io/research-log/gpu.html | 720 × 460 (desktop), ~360 × 560 (mobile) |

The strip is one embed that contains clock, weather, countdown, progress and moon
(each loaded as `…?card=0&compact=1`), plus the greeting, KST date line
(ISO week, day of year) and the quote. On phones it becomes a swipe row at the
same height, so one fixed-height embed works on both.

## Embedding in Notion

1. In a page, type `/embed`, paste the URL, press **Embed link**.
2. Drag the block's bottom edge to the suggested height. Notion sets the width from
   the column the block sits in. Every widget re-flows to whatever box it gets.
3. To lay widgets side by side, drag embeds next to each other to make columns.
   On mobile, Notion stacks columns vertically.

## Updating a widget

1. Edit the file on GitHub (`homelessamy.github.io` → `research-log/<name>.html` → ✏️),
   change the `CONFIG` block at the top of the `<script>`, and commit.
2. GitHub Pages redeploys in about a minute.
3. Notion and the browser may cache the old copy for up to 10 minutes. To force a
   refresh, change the embed URL to add a version: `…/countdown.html?v=2`
   (block menu → **Replace** / edit link).

URL parameters let you reuse one file in several embeds without editing it.

### clock.html
`ZONES` (first entry drives the analog face), `HOUR12`, `SMOOTH_SECONDS`.
Params: `?tz1=Asia/Seoul&tz2=Asia/Karachi` (+ optional `l1`, `a1`, `l2`, `a2` for label/abbr), `?h12=1`.

### timer.html
`CONFIG.focus / short / long` (minutes), `roundsBeforeLong`, `autoStartBreaks`, `chime`.
Params: `?focus=50&short=10&long=20&rounds=4&auto=1&chime=0`.
Precedence: CONFIG < URL params < values saved from the in-widget **settings** sheet
(**defaults** clears them). Keys once the widget has focus: Space start/pause,
R reset, S skip. It uses timestamps, so it stays accurate when the tab is throttled,
and a reload resumes a running session. Completed focus sessions are counted per day (KST).

### spotify.html
`PLAYLIST.id / type / title / height` (152 = compact, 352 = with track list).
Params: `?id=<id>&type=playlist&h=352&title=…`.

### weather.html
`PLACE.name / lat / lon / tz / units` (`metric` or `imperial`), `REFRESH_MINUTES`.
Params: `?lat=&lon=&name=&tz=&units=`. The last response is cached, so the
widget draws instantly and shows "offline · showing HH:MM" if the API is unreachable.

### countdown.html
`DEADLINE = { label, at }`. Use an ISO timestamp **with an offset**, e.g. AoE =
`-12:00`. `START_DAYS_BEFORE` sets where the progress line starts. `DISPLAY_TZ`.
Params: `?to=2027-01-28T23:59:00-12:00&label=ICML%20full%20paper&from=2026-11-01`.
While the label contains "PLACEHOLDER" the widget shows a *placeholder* tag.

### progress.html
`SEMESTER` and `MILESTONE` (`label`, `start`, `end`, inclusive calendar days in `TZ`).
Both currently have `placeholder: true`. Check the dates against the KAIST academic
calendar and your graduation plan, then delete that flag.
Params: `?s1=&e1=&l1=&s2=&e2=&l2=`.

### quote.html
`QUOTES` is an inline list of `{ q, a, s }`, every entry with a named source. One
quote per KST day, in a fixed shuffled order. Click or tap the quote, or press
**next →**, to cycle. Params: `?i=3` pins a quote, `?hidesrc=1` hides sources.

### moon.html
Computed locally with Meeus, *Astronomical Algorithms*: ch. 49 for the true new/full
moon instants and ch. 48 for illumination. It agrees with an astropy ephemeris to
within minutes. `NORTHERN_HEMISPHERE`, `DISPLAY_TZ`. Params: `?south=1`,
`?tz=&abbr=`, `?at=<ISO>` to pin an instant.

### gpu.html
`LEDGER.budget / unit / machine / periodLabel / periodStart / periodEnd` (all
**placeholders**: delete `placeholder: true` once they're real), `burnWindowDays`,
and `PROJECTS` (names + tints). Params: `?budget=&from=&to=&period=`.
It shows hours left, used / budget, a bar with a tick for how much of the period
has elapsed, burn rate over the last 14 days, and the projected run-out date.

### strip.html
`NAME`, `DATE_TZ`, `CELLS` (any of `clock, weather, countdown, progress, moon, timer, gpu`),
`CELL_PARAMS` (extra query per cell, e.g. `countdown: 'to=…&label=…'`), `SHOW_QUOTE`.
Params: `?name=&cells=clock,weather,moon&quote=0&theme=paper`. You can also pass a
cell's query through the strip, e.g. `?countdown=to%3D2027-01-28T23%3A59%3A00-12%3A00`.

## Known Notion limitations

- **Fixed embed height.** Notion doesn't let a page size its own embed, so you set the
  height once by dragging. Widgets fit to any box, but if the box is too small,
  secondary lines hide first.
- **Mobile app.** Embeds work in the Notion iOS/Android apps but can load more slowly
  and may need a tap to activate. Columns stack. The strip switches to a swipe row
  under 620 px wide.
- **Storage is per device.** The timer, GPU ledger and weather cache use
  `localStorage` inside the embed. Data saved on your laptop won't appear on your
  phone, and clearing site data erases it. Use the GPU ledger's **export / import**
  (download, copy, or paste JSON) to move or back up entries. Downloads may be
  blocked inside Notion's sandbox, in which case use **copy**.
- **Spotify inside an embed.** Spotify sits inside this page, inside Notion. Without a
  logged-in Spotify session in that browser context, it plays 30-second previews.
  If full playback doesn't work, use Notion's native Spotify embed:
  `/embed` → `https://open.spotify.com/playlist/5hGkozycxt4V7t75Zb6ROx`.
- **Sound.** The timer's chime needs one click on the widget first (browsers block
  audio until you interact).
- **Theme.** Notion can't tell an embed whether it's in light or dark mode. Widgets
  default to the ink (dark) theme; add `?theme=paper` to embeds on light-mode pages.
- Each page has `noindex`, so search engines won't list these pages on your portfolio domain.
