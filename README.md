# THE WORLD TODAY — Wednesday 25 November 2026

[![Competition](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![Rank](https://make.fun/badge/news-image-20261125/massy-o/world-today-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![Reward](https://make.fun/badge/news-image-20261125/massy-o/world-today-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

A one-page newspaper front page that sums up Wednesday 25 November
2026 in a single 1024×1024 image: six story cards (Nvidia's rally
fizzles, China probes Shanghai's party chief, Kyiv strikes kill 14,
Riyadh's PIF tower hit twice, a UN femicide report, landmine
casualties at a five-year high), a ten-figure numbers strip, and
thirty briefs — 58 sourced facts in all.

## Run it

```
python3 main.py
```

Writes `/output/entry.png` (falls back to `./entry.png` when
`/output` is not writable). Pure Python 3 standard library — the
PNG encoder and the 5×7 pixel typeface are both in `main.py`.
No network access; repeated runs produce byte-identical output.

## How the page was made

The day's wire reports (AP, AFP, Reuters, SCMP, Dow Jones wires)
were gathered into a 51-item candidate pool. Groq's
`openai/gpt-oss-120b` ranked the pool and designed the page, and
`qwen/qwen3.8-27b` sub-edited the draft, correcting two facts
before print. The renderer was then written for this entry and
revised against its own output.

## License

MIT
