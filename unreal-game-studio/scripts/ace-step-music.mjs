#!/usr/bin/env node
// Generate game music with a local ACE-Step 1.5 API server and save it into an
// Unreal project's Content folder. Node 18+, no dependencies.
// Usage: node ace-step-music.mjs --prompt "cozy pixel village, upbeat 8-bit" \
//          --out "C:/MyGame/Content/Audio/Music" [--name village_theme] [--duration 60]
//          [--bpm 120] [--lyrics "..."] [--format wav] [--batch 1] [--timeout 600]
// Env: ACESTEP_URL (default http://localhost:8001), ACESTEP_API_KEY (optional).
import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { parseArgs } from "node:util";

const HELP = `Usage: node ace-step-music.mjs --prompt TEXT --out DIR [options]
  --prompt TEXT     music description (genre, mood, instruments)
  --out DIR         folder to write audio into (e.g. <Game>/Content/Audio/Music)
  --name NAME       file name without extension (default: track)
  --duration SEC    10-600 (default 60)
  --bpm N           30-300 (optional)
  --lyrics TEXT     lyrics; default "[Instrumental]" (no vocals)
  --format FMT      wav (default; Unreal imports WAV natively), flac or mp3
  --batch N         variations to generate, 1-8 (default 1)
  --timeout SEC     give up after this many seconds (default 600)
Env: ACESTEP_URL (default http://localhost:8001), ACESTEP_API_KEY (optional)`;

const { values: a } = parseArgs({
  options: {
    prompt: { type: "string" }, out: { type: "string" }, name: { type: "string", default: "track" },
    duration: { type: "string", default: "60" }, bpm: { type: "string" },
    lyrics: { type: "string", default: "[Instrumental]" }, format: { type: "string", default: "wav" },
    batch: { type: "string", default: "1" }, timeout: { type: "string", default: "600" },
    help: { type: "boolean", short: "h" },
  },
});
if (a.help) { console.log(HELP); process.exit(0); }
if (!a.prompt || !a.out) { console.error(`error: --prompt and --out are required\n\n${HELP}`); process.exit(2); }
if (!/^[\w.-]+$/.test(a.name)) { console.error("error: --name may only contain letters, digits, _ . -"); process.exit(2); }
const FORMATS = new Set(["wav", "flac", "mp3"]);
if (!FORMATS.has(a.format)) { console.error(`error: --format must be one of ${[...FORMATS].join(", ")}`); process.exit(2); }

const base = (process.env.ACESTEP_URL || "http://localhost:8001").replace(/\/+$/, "");
const headers = { "Content-Type": "application/json" };
if (process.env.ACESTEP_API_KEY) headers.Authorization = `Bearer ${process.env.ACESTEP_API_KEY}`;

async function post(path, body) {
  const res = await fetch(base + path, { method: "POST", headers, body: JSON.stringify(body) });
  const json = await res.json().catch(() => null);
  if (!res.ok || !json || (json.code && json.code !== 200)) {
    throw new Error(`${path} failed: HTTP ${res.status} ${json?.error ?? ""}`.trim());
  }
  return json.data;
}

const body = {
  prompt: a.prompt, lyrics: a.lyrics, audio_format: a.format,
  audio_duration: Number(a.duration), batch_size: Number(a.batch), inference_steps: 8,
};
if (a.bpm) body.bpm = Number(a.bpm);

try {
  const { task_id } = await post("/release_task", body);
  console.error(`queued task ${task_id} on ${base}`);
  const deadline = Date.now() + Number(a.timeout) * 1000;
  let item;
  for (;;) {
    [item] = await post("/query_result", { task_id_list: [task_id] });
    if (item?.status === 1) break;
    if (item?.status === 2) throw new Error(`generation failed: ${item.result ?? "no details"}`);
    if (Date.now() > deadline) throw new Error(`timed out after ${a.timeout}s (task ${task_id})`);
    await new Promise((r) => setTimeout(r, 2000));
  }
  const results = typeof item.result === "string" ? JSON.parse(item.result) : item.result;
  await mkdir(a.out, { recursive: true });
  const written = [];
  for (const [i, r] of results.entries()) {
    if (!r.file) continue;
    const res = await fetch(new URL(r.file, base + "/"), { headers });
    if (!res.ok) throw new Error(`download failed: HTTP ${res.status}`);
    const file = join(a.out, `${a.name}${results.length > 1 ? `_${i + 1}` : ""}.${a.format}`);
    await writeFile(file, Buffer.from(await res.arrayBuffer()));
    written.push({ file, bpm: r.metas?.bpm, key: r.metas?.keyscale, duration: r.metas?.duration, seed: r.seed_value });
  }
  if (!written.length) throw new Error("server returned no audio files");
  console.log(JSON.stringify({ task_id, files: written }, null, 2));
} catch (err) {
  console.error(`error: ${err.message}`);
  if (err.message === "fetch failed") console.error(`Is the ACE-Step API server running? Start it with start_api_server.(sh|bat); expected at ${base}`);
  process.exit(1);
}
