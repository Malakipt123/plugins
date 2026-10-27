# Creator Kit

Plugin with four skills for creator workflows: trade ideas tested on paper, videos edited from a folder, motion videos written as code, and websites that look designed.

## What it includes

- `trade-replay`: Scanner → News → Entry → Exit → Time Machine. Replays the rest of the trading day 10,000 times from today's bars (block bootstrap) and reports how often the target or the stop is hit first. Paper only, never places real orders. Script: `skills/trade-replay/scripts/replay.mjs` (Node 18+, no dependencies).
- `video-edit-folder`: sets up `raw footage/`, `references/`, `assets/`, `exports/` and a `CLAUDE.md`, learns the user's style from reference videos into `STYLE.md`, then cuts silences, burns word-level captions and exports vertical video with ffmpeg and faster-whisper.
- `motion-video`: script → scenes → HTML/CSS (or Remotion) animated from a single `seek(t)` function, rendered frame by frame with Playwright and encoded with ffmpeg. Covers mascots, voiceover and music.
- `alive-website`: art direction from real reference sites into `DESIGN.md`, a design vocabulary, a reusable component bank, purposeful Framer Motion animation, and a Playwright screenshot loop at mobile, tablet and desktop widths.

## When to use it

Run `/trade-replay`, `/video-edit-folder`, `/motion-video` or `/alive-website`, or ask for the matching task in plain words.

## Try the replay script

```bash
node creator-kit/skills/trade-replay/scripts/replay.mjs --help
node creator-kit/skills/trade-replay/scripts/replay.mjs --csv bars.csv --entry 100 --target 101 --stop 99 --bars 240
```

The CSV needs a header row with a `close` column, oldest bar first; `high` and `low` columns are used when present.

## License

MIT
