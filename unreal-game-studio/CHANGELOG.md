# Changelog

## 0.3.0

- Added `voice-lines` skill and `scripts/elevenlabs-voice-lines.mjs`: dialogue JSON to 16 kHz mono WAVs per character via ElevenLabs (dry run with character count, skips existing files, stops on first API error, key only from `ELEVENLABS_API_KEY`).
- Added `examples/dialogue.example.json`.
- `facial-animation`: route A (bake in a UE 5.6 face lab, migrate into 5.7) is now the default, with a step-by-step workflow.

## 0.2.0

- Added `audio-artist` agent, `game-music` skill (ACE-Step 1.5) and `facial-animation` skill (NVIDIA Audio2Face-3D, with the UE 5.6 → 5.7 bake route).
- Added `scripts/ace-step-music.mjs` to generate a track on a local ACE-Step server and save the WAV into `Content/`.

## 0.1.0

- Initial release: `unrealclaude` MCP server (Natfii/UnrealClaude bridge), studio agents (creative-director, game-designer, gameplay-programmer, qa-tester), `setup-unrealclaude` and `studio-loop` skills, editor safety rule.
