---
name: game-music
description: Generate original game music and loops locally with ACE-Step 1.5 (text-to-music) and drop the WAV files into an Unreal project. Use when the user wants a soundtrack, level theme, menu music, battle loop or jingle for their game.
---

# Game music with ACE-Step 1.5

[ACE-Step 1.5](https://github.com/ace-step/ACE-Step-1.5) (MIT) is an open text-to-music model that runs on the user's own machine. It serves a REST API on `http://localhost:8001`; this plugin's `scripts/ace-step-music.mjs` calls it and saves the result into the game's `Content` folder.

## Requirements

- NVIDIA GPU recommended (works from ~4 GB VRAM with offload; 8 GB+ is comfortable). AMD ROCm, Intel XPU and Apple Silicon (MLX) are also supported, more slowly.
- Python 3.11-3.12 via `uv` (the repo's install scripts set it up). Models (several GB) download from Hugging Face on first run.

## One-time setup (user runs it on their machine)

```sh
git clone https://github.com/ace-step/ACE-Step-1.5.git
cd ACE-Step-1.5
# Windows: install_uv.bat, then start_api_server.bat
# Linux:   ./install_uv.sh, then ./start_api_server.sh
# macOS:   ./install_uv.sh, then ./start_api_server_macos.sh
```

Wait until the server answers on `http://localhost:8001` (first start downloads the models). Ask the user before installing; it is a large download.

## Generate a track

1. Write the prompt like a music brief: genre, mood, instruments, tempo, and the game moment. Examples:
   - `cozy pixel village, upbeat 8-bit chiptune, square-wave lead, bouncy bass` (town theme)
   - `tense orchestral boss battle, pounding taiko drums, brass stabs, fast` (boss)
   - `calm ambient synth pads, gentle piano, slow, seamless loop` (menu)
2. Run (paths with forward slashes work on Windows too):
   ```sh
   node <plugin>/scripts/ace-step-music.mjs \
     --prompt "cozy pixel village, upbeat 8-bit chiptune" \
     --out "<Game>/Content/Audio/Music" --name village_theme --duration 60 --bpm 120
   ```
   Defaults: instrumental (`[Instrumental]` lyrics), WAV, one variation. Use `--batch 3` to get options and let the user pick. It prints JSON with each file's path, BPM, key and seed.
3. Import into Unreal: with **Editor Preferences → General → Loading & Saving → Auto Reimport → Monitor Content Directories** on (and "Auto Create Assets" enabled), the WAV becomes a Sound Wave by itself; otherwise drag it into the Content Browser. Then check it with `unreal_asset_search`.
4. Hook it up (gameplay-programmer): set the Sound Wave to loop, then play it from the level Blueprint or an Audio component on a manager actor. Use separate tracks per state (explore / combat / menu) and crossfade with Fade In / Fade Out.

## Tips

- Loops: ask for "seamless loop" and trim the start/end in an audio editor if the seam clicks.
- Keep the seed from the JSON output to regenerate the same track with tweaks.
- Generated music is for the user's own game; avoid prompts that name a real artist or copyrighted song.
- If the server is down the script says so; do not try to start it yourself on the user's machine without asking.
