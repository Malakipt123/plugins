---
name: video-edit-folder
description: >-
  Use when the user runs /video-edit-folder or wants an AI video editor in a
  folder: set up raw footage, references, assets and exports folders, install
  ffmpeg and faster-whisper, learn the user's editing style from reference
  videos into STYLE.md, then cut, caption and export short vertical videos
  (TikTok, Reels, Shorts) from raw footage.
---

# Video Edit Folder

Turn a plain folder into a repeatable video editor. The agent learns the user's style once from reference videos, writes it down, and then edits every new raw clip the same way.

## 1. Folder

Create this layout (ask before creating it somewhere other than the current folder):

```
<project>/
  raw footage/   # untouched clips from the phone or camera
  references/    # 2-5 finished videos whose style the user wants to copy
  assets/        # logo, fonts, music, sound effects, b-roll
  exports/       # finished videos, never overwritten
  work/          # transcripts, cut lists, temp renders (safe to delete)
  CLAUDE.md
```

Write `CLAUDE.md` with: the target format (default 1080×1920, 30 fps, H.264 + AAC), the language of the captions, "never modify files in `raw footage/`", "write every export to `exports/` with a new name", and "follow `references/STYLE.md`".

## 2. Tools

Check each and install only what is missing, with the user's OK:

| Tool | Check | Purpose |
| --- | --- | --- |
| ffmpeg / ffprobe | `ffmpeg -version` | cut, scale, burn captions, mix audio |
| faster-whisper | `python -c "import faster_whisper"` | word-level transcript (`pip install faster-whisper`) |
| Remotion (optional) | `npx remotion --version` | animated titles and overlays in React |

On macOS use Homebrew for ffmpeg, on Windows `winget install Gyan.FFmpeg`, on Linux the distro package.

## 3. Learn the style → `references/STYLE.md`

For each reference video:

- `ffprobe` for resolution, fps, duration.
- Scene cuts: `ffmpeg -i ref.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep pts_time` and compute the average shot length.
- A contact sheet to look at: `ffmpeg -i ref.mp4 -vf "fps=1/2,scale=270:-1,tile=4x4" -frames:v 1 work/ref-sheet.jpg`, then view the image.
- The transcript with faster-whisper, to see pacing (words per second) and how the hook is phrased.

Write `STYLE.md` with concrete, checkable rules: hook length, average shot length, caption style (font, size, position, words per line, highlight colour, upper/lower case), zooms or punch-ins, b-roll frequency, music level relative to voice (e.g. −18 dB), and the ending. Show it to the user and adjust before editing.

## 4. Edit a raw clip

1. Transcribe with word timestamps into `work/<clip>.json`.
2. Build a cut list in `work/<clip>-cuts.json`: remove silences over 0.4 s, false starts and repeated takes (keep the last good take). Show the kept text to the user before rendering when the cut removes more than a quarter of the clip.
3. Render the cuts with ffmpeg (`trim`/`atrim` + `concat`, or the `select` filter), scaled and cropped to the target format.
4. Captions: generate an `.ass` file from the word timestamps following `STYLE.md` and burn it with `-vf ass=work/<clip>.ass`.
5. Music from `assets/` with side-chain ducking under the voice (`sidechaincompress`), at the level in `STYLE.md`.
6. Export to `exports/<clip>-v1.mp4` (`-c:v libx264 -crf 20 -preset medium -c:a aac -b:a 160k -movflags +faststart`). Bump the version for every new render.

## 5. Check before handing over

Make a contact sheet of the export and view it: captions inside the safe area (not under the platform's buttons on the right and bottom), no black bars, no cut mid-word. Report the duration, what was cut, and the export path.
