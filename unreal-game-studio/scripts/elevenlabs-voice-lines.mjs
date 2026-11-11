#!/usr/bin/env node
// Turn a dialogue table into voice-line WAVs with ElevenLabs text-to-speech,
// ready for Unreal and NVIDIA Audio2Face-3D (16 kHz, mono, 16-bit PCM).
// Node 18+, no dependencies. API key from ELEVENLABS_API_KEY (never a file).
//
// Usage:
//   node elevenlabs-voice-lines.mjs --list-voices
//   node elevenlabs-voice-lines.mjs --script Design/dialogue.json \
//        --out "C:/MyGame/Content/Audio/Voice" [--dry-run] [--force]
//
// dialogue.json:
// {
//   "model": "eleven_multilingual_v2",          (optional)
//   "voices": { "Elder": "<voice_id>", "Guard": "<voice_id>" },
//   "lines": [
//     { "id": "elder_greet_01", "character": "Elder", "text": "Welcome, traveler.",
//       "voice_settings": { "stability": 0.4, "style": 0.3 } }      (optional)
//   ]
// }
import { mkdir, readFile, writeFile, access } from "node:fs/promises";
import { join } from "node:path";
import { parseArgs } from "node:util";

const HELP = `Usage:
  node elevenlabs-voice-lines.mjs --list-voices
  node elevenlabs-voice-lines.mjs --script FILE --out DIR [--dry-run] [--force] [--rate 16000]
    --script FILE  dialogue JSON (voices map + lines with id, character, text)
    --out DIR      writes DIR/<character>/<id>.wav (e.g. <Game>/Content/Audio/Voice)
    --dry-run      show what would be generated and the character count; no API calls
    --force        regenerate files that already exist (default: skip them, saves credits)
    --rate HZ      16000 (default, best for Audio2Face), 22050, 24000 or 44100
Env: ELEVENLABS_API_KEY (required except for --dry-run), ELEVENLABS_BASE_URL (default https://api.elevenlabs.io/v1)`;

const { values: a } = parseArgs({
  options: {
    script: { type: "string" }, out: { type: "string" }, rate: { type: "string", default: "16000" },
    "dry-run": { type: "boolean" }, force: { type: "boolean" }, "list-voices": { type: "boolean" },
    help: { type: "boolean", short: "h" },
  },
});
const fail = (msg, code = 1) => { console.error(`error: ${msg}`); process.exit(code); };
if (a.help) { console.log(HELP); process.exit(0); }

const base = (process.env.ELEVENLABS_BASE_URL || "https://api.elevenlabs.io/v1").replace(/\/+$/, "");
const key = process.env.ELEVENLABS_API_KEY;
const needKey = () => { if (!key) fail("set ELEVENLABS_API_KEY in your environment (do not put it in files)", 2); };

async function api(path, init = {}) {
  const res = await fetch(base + path, { ...init, headers: { "xi-api-key": key, ...init.headers } });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`${path.split("?")[0]} -> HTTP ${res.status} ${detail.slice(0, 300)}`);
  }
  return res;
}

if (a["list-voices"]) {
  needKey();
  const { voices = [] } = await (await api("/voices")).json();
  for (const v of voices) console.log(`${v.voice_id}\t${v.name}\t${Object.values(v.labels ?? {}).join(", ")}`);
  process.exit(0);
}

if (!a.script || !a.out) fail(`--script and --out are required\n\n${HELP}`, 2);
const RATES = new Set(["16000", "22050", "24000", "44100"]);
if (!RATES.has(a.rate)) fail(`--rate must be one of ${[...RATES].join(", ")}`, 2);
const rate = Number(a.rate);

let doc;
try { doc = JSON.parse(await readFile(a.script, "utf8")); } catch (e) { fail(`cannot read ${a.script}: ${e.message}`, 2); }
const voices = doc.voices ?? {};
const lines = Array.isArray(doc.lines) ? doc.lines : fail("script needs a \"lines\" array", 2);
const model = doc.model || "eleven_multilingual_v2";
const SAFE = /^[\w.-]+$/;

// Validate everything before spending any credits.
const problems = [];
const seen = new Set();
lines.forEach((l, i) => {
  const where = `lines[${i}]${l?.id ? ` (${l.id})` : ""}`;
  if (!l?.id || !SAFE.test(l.id)) problems.push(`${where}: id must be letters, digits, _ . -`);
  else if (seen.has(l.id)) problems.push(`${where}: duplicate id`);
  seen.add(l?.id);
  if (!l?.character || !SAFE.test(l.character)) problems.push(`${where}: character must be letters, digits, _ . -`);
  else if (!voices[l.character]) problems.push(`${where}: no voice_id for character "${l.character}" in "voices"`);
  if (!l?.text?.trim()) problems.push(`${where}: empty text`);
});
if (problems.length) fail(`script has problems:\n  ${problems.join("\n  ")}`, 2);

const exists = (f) => access(f).then(() => true, () => false);
const todo = [];
for (const l of lines) {
  const file = join(a.out, l.character, `${l.id}.wav`);
  if (!a.force && (await exists(file))) continue;
  todo.push({ ...l, file });
}
const chars = todo.reduce((n, l) => n + l.text.length, 0);
console.error(`${todo.length} of ${lines.length} lines to generate (${chars} characters, model ${model}, ${rate} Hz)`);
if (a["dry-run"]) {
  for (const l of todo) console.log(`${l.file}\t${l.character}\t${l.text}`);
  process.exit(0);
}
if (!todo.length) process.exit(0);
needKey();

function wav(pcm, sampleRate) {
  const h = Buffer.alloc(44);
  h.write("RIFF", 0); h.writeUInt32LE(36 + pcm.length, 4); h.write("WAVE", 8);
  h.write("fmt ", 12); h.writeUInt32LE(16, 16); h.writeUInt16LE(1, 20); h.writeUInt16LE(1, 22);
  h.writeUInt32LE(sampleRate, 24); h.writeUInt32LE(sampleRate * 2, 28); h.writeUInt16LE(2, 32); h.writeUInt16LE(16, 34);
  h.write("data", 36); h.writeUInt32LE(pcm.length, 40);
  return Buffer.concat([h, pcm]);
}

const done = [];
for (const l of todo) {
  const body = { text: l.text, model_id: model };
  if (l.voice_settings) body.voice_settings = l.voice_settings;
  try {
    const res = await api(`/text-to-speech/${encodeURIComponent(voices[l.character])}?output_format=pcm_${rate}`, {
      method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body),
    });
    const pcm = Buffer.from(await res.arrayBuffer());
    await mkdir(join(a.out, l.character), { recursive: true });
    await writeFile(l.file, wav(pcm, rate));
    done.push({ id: l.id, file: l.file, seconds: +(pcm.length / 2 / rate).toFixed(2) });
    console.error(`ok  ${l.id}`);
  } catch (e) {
    console.error(`FAIL ${l.id}: ${e.message}`);
    console.log(JSON.stringify({ written: done, failed: l.id }, null, 2));
    process.exit(1); // stop on first error so a bad key or quota does not burn through the list
  }
}
console.log(JSON.stringify({ written: done }, null, 2));
