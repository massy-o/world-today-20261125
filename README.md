# THE WORLD TODAY — Wednesday 25 November 2026 (dense edition)

[![Competition](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![Rank](https://make.fun/badge/news-image-20261125/massy-o/world-today-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![Reward](https://make.fun/badge/news-image-20261125/massy-o/world-today-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

One page that sums up Wednesday 25 November 2026 — packed tighter
than the previous edition: a smaller masthead and headlines, fuller
card copy, and forty briefs instead of thirty. Around 82 sourced
facts in a single 1024×1024 image: six story cards (Nvidia's rally
fizzles, China probes Shanghai's party chief, Kyiv strikes kill 14,
Riyadh's PIF tower is hit twice, a UN femicide report, landmine
casualties at a five-year high), each with a second-angle line, a
ten-figure numbers strip, and forty briefs.

## Run it

    python3 main.py

Writes `/output/entry.png`. Pure Python 3 standard library — the
PNG encoder and the 5×7 pixel typeface are both in `main.py`.
No network access; two runs produce byte-identical output.

## How the page was made

The day's wire reports (AP, AFP, Reuters, SCMP, Dow Jones wires)
were collected into a 51-item candidate pool. Groq's
`gpt-oss-120b` ranked the pool and designed the page; `qwen3.8-27b`
sub-edited the draft and corrected two facts before print. This
edition reworks the layout for density: the renderer was rewritten
from scratch and revised against its own output.

## License

MIT
