#!/usr/bin/env node
// Monte Carlo "time machine" for a paper trade: replays the rest of the day
// many times by bootstrapping the bar-to-bar returns seen so far, and counts
// how often the target or the stop is touched first. Paper analysis only.

import { readFileSync, realpathSync } from "fs";
import { fileURLToPath } from "url";

const HELP = `Usage: replay.mjs --csv <bars.csv> --entry <price> --target <price> --stop <price> [options]

Options:
  --csv <file>       Bars so far, oldest first. Needs a "close" column (high/low used when present).
  --entry <price>    Entry price of the paper trade.
  --target <price>   Take-profit price.
  --stop <price>     Stop-loss price.
  --bars <n>         Bars left in the session (default: same as bars in the CSV).
  --runs <n>         Number of replays (default: 10000).
  --block <n>        Block length for the bootstrap, keeps short-term momentum (default: 5).
  --seed <n>         Seed for repeatable results (default: 42).
  --json             Print JSON instead of a text summary.
  -h, --help         Show this help.

Example:
  replay.mjs --csv aapl-1m.csv --entry 189.2 --target 191 --stop 188.3 --bars 240`;

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "-h" || a === "--help") args.help = true;
    else if (a === "--json") args.json = true;
    else if (a.startsWith("--")) args[a.slice(2)] = argv[++i];
    else throw new Error(`Unexpected argument: ${a}`);
  }
  return args;
}

function readBars(path) {
  const lines = readFileSync(path, "utf-8").trim().split(/\r?\n/);
  const header = lines[0].split(",").map((h) => h.trim().toLowerCase());
  const col = (name) => header.indexOf(name);
  const ci = col("close");
  if (ci < 0) throw new Error(`${path}: no "close" column in header`);
  const hi = col("high");
  const lo = col("low");
  const bars = lines.slice(1).map((line, n) => {
    const cells = line.split(",");
    const close = Number(cells[ci]);
    if (!Number.isFinite(close) || close <= 0) {
      throw new Error(`${path}: bad close on line ${n + 2}`);
    }
    return {
      close,
      high: hi >= 0 ? Number(cells[hi]) : close,
      low: lo >= 0 ? Number(cells[lo]) : close,
    };
  });
  if (bars.length < 3) throw new Error(`${path}: need at least 3 bars`);
  return bars;
}

// mulberry32: small, fast, seedable
function rng(seed) {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function replay({ bars, entry, target, stop, barsLeft, runs, block, seed }) {
  const long = target > entry;
  if (long ? !(stop < entry) : !(stop > entry)) {
    throw new Error("stop must be on the other side of entry from target");
  }

  // Per-bar log return of the close, plus how far the high and low reached
  // past the close in that bar, so simulated bars keep realistic wicks.
  const steps = [];
  for (let i = 1; i < bars.length; i++) {
    const prev = bars[i - 1].close;
    const b = bars[i];
    steps.push({
      r: Math.log(b.close / prev),
      up: Math.log(Math.max(b.high, b.close) / b.close),
      down: Math.log(b.close / Math.min(b.low, b.close)),
    });
  }

  const rand = rng(seed);
  const len = Math.max(1, Math.min(block, steps.length));
  let hitTarget = 0;
  let hitStop = 0;
  const endPrices = new Float64Array(runs);

  for (let run = 0; run < runs; run++) {
    let price = entry;
    let outcome = 0;
    let k = 0;
    let start = 0;
    for (let t = 0; t < barsLeft && outcome === 0; t++) {
      if (k === 0) start = Math.floor(rand() * (steps.length - len + 1));
      const s = steps[start + k];
      k = (k + 1) % len;
      price *= Math.exp(s.r);
      const high = price * Math.exp(s.up);
      const low = price / Math.exp(s.down);
      const touchedTarget = long ? high >= target : low <= target;
      const touchedStop = long ? low <= stop : high >= stop;
      // Both inside one bar: order is unknown, count it as the stop (conservative).
      if (touchedStop) outcome = -1;
      else if (touchedTarget) outcome = 1;
    }
    if (outcome === 1) hitTarget++;
    else if (outcome === -1) hitStop++;
    endPrices[run] = outcome === 1 ? target : outcome === -1 ? stop : price;
  }

  endPrices.sort();
  const pct = (n) => Math.round((n / runs) * 1000) / 10;
  const quantile = (q) => endPrices[Math.min(runs - 1, Math.floor(q * runs))];
  const reward = Math.abs(target - entry);
  const risk = Math.abs(entry - stop);
  const sign = long ? 1 : -1;
  let pnl = 0;
  for (const p of endPrices) pnl += sign * (p - entry);

  return {
    runs,
    barsLeft,
    side: long ? "long" : "short",
    hitTargetPct: pct(hitTarget),
    hitStopPct: pct(hitStop),
    neitherPct: pct(runs - hitTarget - hitStop),
    rewardToRisk: Math.round((reward / risk) * 100) / 100,
    // Exits at target or stop when touched, otherwise at the simulated close.
    expectedPnlPerShare: Math.round((pnl / runs) * 10000) / 10000,
    endPrice: { p10: quantile(0.1), p50: quantile(0.5), p90: quantile(0.9) },
  };
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(HELP);
    return;
  }
  for (const k of ["csv", "entry", "target", "stop"]) {
    if (args[k] === undefined) throw new Error(`Missing --${k}. Run with --help.`);
  }
  const bars = readBars(args.csv);
  const result = replay({
    bars,
    entry: Number(args.entry),
    target: Number(args.target),
    stop: Number(args.stop),
    barsLeft: Number(args.bars ?? bars.length),
    runs: Number(args.runs ?? 10000),
    block: Number(args.block ?? 5),
    seed: Number(args.seed ?? 42),
  });
  if (args.json) {
    console.log(JSON.stringify(result, null, 2));
    return;
  }
  const f = (p) => p.toFixed(2);
  console.log(`${result.runs} replays of the next ${result.barsLeft} bars (${result.side}, paper only)`);
  console.log(`  hit target first: ${result.hitTargetPct}%`);
  console.log(`  hit stop first:   ${result.hitStopPct}%`);
  console.log(`  neither:          ${result.neitherPct}%`);
  console.log(`  reward/risk:      ${result.rewardToRisk}`);
  console.log(`  expected P&L per share: ${result.expectedPnlPerShare}`);
  console.log(`  end price p10/p50/p90: ${f(result.endPrice.p10)} / ${f(result.endPrice.p50)} / ${f(result.endPrice.p90)}`);
}

// Compared as resolved paths so it also works on Windows and through symlinks.
const invokedDirectly = process.argv[1] && realpathSync(process.argv[1]) === realpathSync(fileURLToPath(import.meta.url));
if (invokedDirectly) {
  try {
    main();
  } catch (err) {
    console.error(`error: ${err.message}`);
    process.exit(1);
  }
}
