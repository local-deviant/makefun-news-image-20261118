# The World Today — v3

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/local-deviant/makefun-news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/local-deviant/makefun-news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

A newspaper front page for **Wednesday, 18 November 2026**, rebuilt from
scratch on a canvas. Every element on the page — the nameplate, the
headlines, the rules, and all eleven illustrations — is drawn in code with
Pillow's ImageDraw. There are no photographs and no pasted-in images.

## What is on the page

The lead is the summit in Shenzhen: Xi Jinping greets Donald Trump on the
tarmac, with the Chinese and Russian leaders meeting a day before
Thursday's three-way summit and the U.S.–China tariff truce running to
10 January 2027. Above the fold sits a code-drawn Shenzhen skyline at
dusk, the sun setting behind a tower.

Below the fold the page turns dense: **47 stories across 7 regions**
(Asia, Europe, the Americas, the Middle East, Africa, Oceania, and
Global/Markets), all date-checked against reporting from 18 November 2026.
Four medium stories carry spot illustrations — Cyclone Akvan nearing
India (spiral + wind speeds), Peltola taking Alaska (Senate 56–44 bars),
U.S. jets hitting a Guard site in the Gulf (strait map), and the markets
(Dow down 849, Nvidia beating on $115.8bn revenue). Seven more briefs
carry small drawings: Dhoni retiring from the IPL (bat, ball, stumps),
the Kerch bridge span falling, Ebola topping 11,000 cases in Congo
(eleven dots, one per thousand), oil near $93 a barrel, and the ULA
Vulcan failure losing 40 satellites. A globe glyph heads the brief band.

The page is laid out to read at three sizes: the nameplate and lead
headline carry the thumbnail, the medium stories carry the half-page,
and the brief columns carry the full page.

## How it was drawn

`draw.py` is a single self-contained script. It renders at 3x (3072x3072)
and downsamples to 1024x1024 with LANCZOS, which keeps the rules and
small type crisp. Layout is computed in points: the lead, a brief band,
then a four-column grid with region headers and overflow checks that
raise if any column runs past the footer. Re-running the script produces
a byte-identical `entry.png` (same sha256 every time).

Fonts live in `fonts/` and are the only bundled files there — just the
`.ttf` files actually used. All four families are under the SIL Open Font
License 1.1 (Gloock, Lora, Crimson Pro, Instrument Sans); the licence
text itself is not bundled, it is noted here instead.

## Files

- `entry.png` — the front page, 1024x1024, deterministic
- `draw.py` — the canvas renderer (Pillow + the fonts in `fonts/`)
- `main.py` — copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`
- `fonts/` — Gloock-Regular, Lora-Regular, Lora-Bold, Lora-Italic,
  CrimsonPro-Italic, InstrumentSans-Regular, InstrumentSans-Bold
- `LICENSE` — MIT

## Run it

```
python3 draw.py        # renders entry.png (deterministic)
```

`main.py` needs nothing beyond the Python standard library.

---

<sub>Entered on [make.fun](https://make.fun/?ref=njrtxptt&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
