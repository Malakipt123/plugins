---
name: voice-lines
description: Generate character voice lines for an Unreal game with ElevenLabs text-to-speech from a dialogue table, as 16 kHz mono WAVs ready for Audio2Face-3D lip-sync. Use when the user wants NPC dialogue, narration or barks voiced with ElevenLabs.
---

# Voice lines with ElevenLabs

`scripts/elevenlabs-voice-lines.mjs` turns a dialogue JSON into one WAV per line at `<out>/<Character>/<id>.wav`: 16 kHz, mono, 16-bit, which is what Audio2Face-3D expects and what Unreal imports as a Sound Wave.

## Key

The user's ElevenLabs API key goes in the `ELEVENLABS_API_KEY` environment variable on their machine. Never write it into the dialogue file, the project, this plugin or a chat message. If it is missing, the script stops before calling the API.

## Steps

1. **Pick voices.** `node <plugin>/scripts/elevenlabs-voice-lines.mjs --list-voices` prints `voice_id`, name and labels from the user's ElevenLabs library. Let the user choose one voice per character (or design one in the ElevenLabs app).
2. **Write the dialogue** in `Design/dialogue.json`, starting from `examples/dialogue.example.json`:
   - `voices`: character → voice_id.
   - `lines`: `id` (becomes the file name, e.g. `elder_greet_01`), `character`, `text`, optional `voice_settings` (`stability` lower = more expressive, `style` higher = more emotional).
   - `model`: `eleven_multilingual_v2` by default (good for Portuguese and other languages).
3. **Dry run** to check the file list and the character count (ElevenLabs bills by characters):
   ```sh
   node <plugin>/scripts/elevenlabs-voice-lines.mjs --script Design/dialogue.json --out "<Game>/Content/Audio/Voice" --dry-run
   ```
   Show the count to the user before generating.
4. **Generate** with the same command without `--dry-run`. Existing files are skipped, so re-running only fills gaps; use `--force` to redo a line after editing its text. The script stops on the first API error (bad key, quota, unknown voice) and prints what was written.
5. **Import** into Unreal (auto-import from the Content folder, or drag into the Content Browser) and check with `unreal_asset_search`.
6. **Faces:** pass the WAVs to the `facial-animation` skill (route A: bake in UE 5.6, migrate into 5.7).

## Tips

- Write for the ear: short sentences, punctuation for pauses, `...` for hesitation.
- Keep one id per line forever; change text, not ids, so Blueprints and animations keep their references.
- Re-generate a single line by deleting its WAV and running again.
