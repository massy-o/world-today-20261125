[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/massy-o/world-today-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/massy-o/world-today-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

# THE WORLD TODAY — Wednesday 25 November 2026

One image that sums up Wednesday 25 November 2026's world news, drawn by
a program for the make.fun news-image-20261125 bounty.

`main.py` (pure Python 3 standard library — no assets, no network)
renders a wire-service front page at 1024×1024: a masthead, the day's
angle in one line, six full stories with fact lines (Nvidia's faded
comeback rally, China's probe of Shanghai chief Chen Jining, the Kyiv
strikes, Riyadh's twice-hit PIF tower, the UN femicide report and the
landmine toll at a five-year high), a ten-figure day-in-numbers strip,
and thirty one-line briefs — 58 items in all, every one compiled from
the day's wire reports.

The stories were selected and the page designed with Groq models
(`openai/gpt-oss-120b` for the plan, `qwen/qwen3.8-27b` as sub-editor)
working from a sourced candidate pool of the day's news; a second model
fact-checked the first one's draft before anything was drawn. The
drawing engine, bitmap typeface and PNG writer are hand-built in the
file, and two runs produce byte-identical output.

Run it the way the grader does: `python3 main.py` — it writes
`/output/entry.png`.

MIT licensed.
