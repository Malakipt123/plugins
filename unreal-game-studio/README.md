# Unreal Game Studio

Make Unreal Engine 5.7 games with a small agent studio that works directly in the open editor.

- **MCP server `unrealclaude`**: connects to the [UnrealClaude](https://github.com/Natfii/UnrealClaude) editor plugin (MIT) over `localhost:3000`. Tools: spawn/move/delete actors, set properties, open levels, search assets, edit Blueprints and Animation Blueprints, Enhanced Input, materials, output log and viewport capture.
- **Agents**: `creative-director` (brief and scope), `game-designer` (mechanics, tuning, layout), `gameplay-programmer` (builds it in the editor), `audio-artist` (music, voice lines, talking faces), `qa-tester` (checks acceptance criteria with logs and screenshots).
- **Skills**: `setup-unrealclaude` (install and connect), `studio-loop` (brief → spec → build → QA → iterate), `game-music` (local text-to-music with [ACE-Step 1.5](https://github.com/ace-step/ACE-Step-1.5)), `voice-lines` (dialogue to WAV with ElevenLabs), `facial-animation` (lip-sync from voice with [NVIDIA Audio2Face-3D](https://github.com/NVIDIA/Audio2Face-3D)).
- **Scripts** (Node 18+, no dependencies, `--help` for options): `scripts/ace-step-music.mjs` asks a local ACE-Step server for a track; `scripts/elevenlabs-voice-lines.mjs` turns `Design/dialogue.json` (see `examples/dialogue.example.json`) into 16 kHz mono WAVs per character. Both save into the game's `Content/`.
- **Rule**: `unreal-editor-safety`.

## Setup

1. Build and install UnrealClaude in your game's `Plugins/` folder and run `npm install` in `Plugins/UnrealClaude/Resources/mcp-bridge` (see the `setup-unrealclaude` skill).
2. Set the plugin variable `UNREALCLAUDE_PLUGIN_DIR` to that `Plugins/UnrealClaude` folder.
3. Open the project in Unreal Editor 5.7 and ask: "Make a small 3D platformer level with a coin to collect."

## Music and faces (optional)

- **Music**: install ACE-Step 1.5 and run its API server (`start_api_server`), then ask "make a cozy 8-bit theme for the village". Needs a GPU (about 4 GB VRAM minimum, 8 GB+ recommended); models download on first run.
- **Voices**: set `ELEVENLABS_API_KEY` in your environment, list voices with `--list-voices`, write the dialogue JSON and run the script (dry run first to see the character count).
- **Faces**: NVIDIA's ACE Unreal plugin targets UE 5.4-5.6, not 5.7. The `facial-animation` skill bakes the animation in a small 5.6 "face lab" project and migrates it into the 5.7 game. Needs an NVIDIA RTX GPU.

## Notes

- Requires Unreal Engine 5.7 and Node.js 18+. The editor must be open for the tools to work.
- No API keys in the plugin: UnrealClaude and ACE-Step run locally; the ElevenLabs key (and an NVIDIA NIM key, if used) comes from environment variables.
- Script execution stays hidden and permission-gated; keep "Auto-approve script execution" off.
