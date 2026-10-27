---
name: trade-replay
description: >-
  Use when the user runs /trade-replay or wants to stress-test a stock or
  crypto trade idea on paper: scan for setups, check news, pick entry, target
  and stop, then replay the rest of the day thousands of times (Monte Carlo)
  to see how often the target or the stop is hit first. Also for following a
  public investor's disclosed trades in a paper portfolio. Paper trading only:
  never places real orders.
---

# Trade Replay

A paper-trading workflow in five steps: **Scanner → News → Entry → Exit → Time Machine**. The last step runs `scripts/replay.mjs`, which replays the rest of the session 10,000 times from the bars seen so far and reports how often the target or the stop is touched first.

## Hard rules

- **Paper only.** Never connect to a live brokerage account, never place, modify or cancel a real order, and never move money, even if asked. If the user wants live trading, say this skill does not do it and stop.
- **Not advice.** Results describe a simulation of past volatility, not a forecast. Say so once in the summary, plainly, without a wall of disclaimers.
- **Real data only.** Every price, headline and filing you cite comes from a tool call or a file the user gave you in this session. Never invent quotes, news or insider trades. If no data source is connected, ask the user for a CSV export.
- Do not paste API keys in chat or commit them.

## Steps

1. **Scanner.** Ask for the market (stocks, crypto) and the timeframe (1-minute or 5-minute bars). With a connected market-data tool, list a handful of candidates with unusual volume or range today and why. Without one, ask the user for tickers.
2. **News.** For the chosen ticker, pull today's headlines and any filings from the connected tools. Summarise in three bullets with the source and time of each. No source: say "no news source connected" and continue.
3. **Entry.** Get the intraday bars so far as CSV with at least a `close` column (`high` and `low` improve the result). Propose an entry, a target and a stop from the chart structure (recent high/low, VWAP if available) and show the reward/risk. The user confirms or changes the numbers.
4. **Exit.** Confirm the exit rule: target, stop, or flat at the close if neither is touched. Ask how many bars are left in the session.
5. **Time Machine.** Run:

   ```bash
   node <skill-dir>/scripts/replay.mjs --csv bars.csv --entry 189.2 --target 191 --stop 188.3 --bars 240 --json
   ```

   `--runs` (default 10000), `--block` (bootstrap block length, default 5) and `--seed` (default 42) are optional. Run `--help` for all flags.

## Reporting

Report in this shape:

| Outcome | Share of replays |
| --- | --- |
| Target first | 29.4% |
| Stop first | 25.5% |
| Neither (flat at close) | 45.1% |

Then one line each for reward/risk, expected P&L per share, and the p10/p50/p90 end price. Close with what would change the picture (a tighter stop, a nearer target, more bars) and offer to rerun with those numbers.

## How the replay works

The script takes the bar-to-bar log returns seen so far today and resamples them in blocks (block bootstrap), so short bursts of momentum survive. Each simulated bar also keeps the wick sizes of its source bar, so a target or stop can be touched inside a bar. When one bar touches both, it counts as the stop, which is the conservative choice. It assumes the rest of the day looks like the part already seen: say this when the morning was unusually quiet or wild.

## Following an investor (paper)

When the user wants to mirror a public investor's disclosed trades (insider filings, congressional disclosures, 13F), use only a connected data tool or files the user provides. Keep a paper portfolio in a local `paper-portfolio.csv` (date, ticker, side, quantity, price, source). Note that disclosures are published days or weeks after the trade, so the paper fill uses the price on the disclosure date, not the original one.
