# THE WORLD TODAY — Wednesday 25 November 2026

[![Competition](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![Rank](https://make.fun/badge/news-image-20261125/massy-o/world-today-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![Reward](https://make.fun/badge/news-image-20261125/massy-o/world-today-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

One page that sums up Wednesday 25 November 2026 in a single 1024×1024 image:
markets wobbling, geopolitics flaring, and the human costs rising — now with
the visual layer the story deserves.

## What's on the page

- **The Day on the Map** — a dotted world map drawn in code from a
  hand-typed landmass grid, with labelled pins for the day's story
  locations: New York, Bogota, London, Kyiv, Gaza, Riyadh, Delhi,
  Myanmar, Beijing, Seoul.
- **Dateline sweep** — the day's cities ordered west to east under the map.
- **Six story cards**, each with its own drawn silhouette art (a fading
  rally chart, a state hall, a domed skyline, a landmark tower, five
  candles, a mined-field warning sign), a source tag (Reuters, AP, SCMP,
  UN, Ukraine officials, global report), a compact headline, a fuller
  body, and an accent second-angle line:
  Nvidia's slide, Beijing's probe of Chen Jining, the Kyiv strikes,
  Riyadh's PIF tower hit twice, the UN femicide report, and landmine
  casualties at a five-year high of 7,000.
- **The Day in Numbers** — ten figures: $237bn Venezuela debt, 7,000 mine
  casualties, 14 killed at Kyiv, 25 hostages in Colombia, Nvidia −6%,
  Nasdaq −1.5%, S&P 500 −0.5%, confidence 103.3, the $100M Shein deal,
  and 81.5M US travellers.
- **In Brief, grouped by region** — 36 more facts under Europe,
  Asia-Pacific, Americas, Middle East + Africa, and World headers.

In total the page carries roughly 85 items and facts, every one of them
sourced from the day's wire reports (AP, AFP, Reuters, SCMP, Dow Jones).

## How it works

`main.py` is a single self-contained Python 3 program using only the
standard library — no network, no third-party packages, fully
deterministic (byte-identical output on every run). It implements
everything itself:

- a minimal PNG encoder (zlib + CRC chunks),
- a hand-drawn 5×7 pixel typeface,
- the dotted world map, projected from longitude/latitude,
- the card art, drawn from rectangle/line/circle primitives,
- the complete front-page layout.

## Run it

```sh
python3 main.py
```

Writes the image to `/output/entry.png` (falling back to `./entry.png`
when `/output` is not writable).

## Competition

Entry for [news-image-20261125](https://make.fun/bounty/news-image-20261125)
on make.fun — "Sum up 25 November's world news in one image."
