# news-image-20261124 — The World Today

[![news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/c/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/pempek2876-maker/news-image-20261124/rank.svg)](https://make.fun/c/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/pempek2876-maker/news-image-20261124/reward.svg)](https://make.fun/c/news-image-20261124)

Entry for the [make.fun competition "Sum up 24 November's world news in one image"](https://make.fun/c/news-image-20261124).

`main.py` (Python 3.13, standard library only, no network) draws an illustrated
newspaper front page — **THE WORLD TODAY, Tuesday, 24 November 2026** — as a
deterministic 1024×1024 PNG:

- **Hero:** Tokyo reopens after Friday's rout — Nikkei futures point near +3%
  as the exchange returns from its holiday; Monday on Wall Street: S&P +4.7%,
  Nasdaq +6.5%, Dow +3.0%, Nvidia +30% as Huang returns as CEO.
- **COP31:** no deal in Antalya, no surrender — Erdogan: "all is not lost",
  46 decisions adopted, talks go on.
- **Tech:** Korea chip exports +294% in the first 20 days of November.
- **Sport:** Sinner under the knife today — knee surgery in Turku, Finland;
  3–4 months out, Melbourne in doubt.
- **Also in the news:** Kyiv strikes, Congo cobalt halt, CrowdStrike–Zscaler
  $43.9B, Syria training talks, India rice duties, West Bank, US House 258,
  Don Toliver concert evacuation. Ticker: oil falls as Trump gives Iran talks
  more time.

## Run

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

Two runs write byte-identical output. The program reads nothing but its own
source and writes only `/output/entry.png` (or `$MAKEFUN_OUTPUT_DIR/entry.png`).

## License

MIT — see [LICENSE](LICENSE).
