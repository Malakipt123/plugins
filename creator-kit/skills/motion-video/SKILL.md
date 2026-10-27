---
name: motion-video
description: >-
  Use when the user runs /motion-video or wants an animated explainer, motion
  graphics, kinetic text, an animated mascot or a product promo made from a
  script, with no camera footage: write each scene as HTML/CSS/JS (or React
  with Remotion), render it frame by frame to MP4, and add voiceover and
  music. Also for HeyGen HyperFrames-style videos.
---

# Motion Video

Make a whole video from a script with code: each scene is an HTML page (or a Remotion component) animated on a timeline, rendered to frames, and encoded with ffmpeg. Everything stays editable as text.

## Pick the engine

| Engine | Use when |
| --- | --- |
| **HTML + Playwright** (default) | No React setup wanted. One HTML file per scene, CSS/JS animation driven by a time variable. |
| **Remotion** | The project already uses React, or the user wants a preview player and reusable components. `npx create-video@latest`. |
| **HyperFrames (HeyGen)** | The user asks for it by name. Read its current docs first; do not guess its API. |

## Script → scenes

1. Write `script.md`: one line per scene with the spoken text, what is on screen, and the duration. Default format 1080×1920, 30 fps; ask if it is for YouTube (1920×1080).
2. Hook in the first 2 seconds, one idea per scene, 3-6 seconds per scene, and on-screen text short enough to read in half the scene's time.
3. Show the scene list to the user before animating.

## Deterministic animation (HTML engine)

Never animate with real time (`setTimeout`, CSS animations running on their own): a renderer that skips or stalls would change the video. Drive everything from one function:

```html
<script>
  // The renderer calls window.seek(t) with t in seconds before each screenshot.
  const ease = (x) => 1 - Math.pow(1 - x, 3);
  const clamp = (x) => Math.min(1, Math.max(0, x));
  window.seek = (t) => {
    const p = ease(clamp((t - 0.2) / 0.6));
    title.style.opacity = p;
    title.style.transform = `translateY(${(1 - p) * 40}px)`;
  };
</script>
```

Render with Playwright (`chromium.launch()`, viewport at the target size, `deviceScaleFactor: 1`): for each frame `n`, call `page.evaluate(t => window.seek(t), n / fps)`, then `page.screenshot({ path: frames/%05d.png })`. Wait for `document.fonts.ready` before the first frame. Encode:

```bash
ffmpeg -framerate 30 -i frames/%05d.png -c:v libx264 -pix_fmt yuv420p -crf 18 scene-01.mp4
```

Join the scenes with the concat demuxer, then add audio.

## Mascot or character

For a recurring character (like a pixel-art mascot), draw it once as SVG with named groups (`#eyes`, `#mouth`, `#arms`) and animate those groups per expression: blink, talk (mouth open/closed on the voice's loud frames), jump, wave. Keep a small sheet of expressions in `assets/mascot.svg` so every video reuses it.

## Voice and music

- Voiceover from any TTS the user has connected (ElevenLabs, Grok TTS). Time each scene to its line: scene duration = audio duration + 0.3 s.
- Music under the voice at about −18 dB, ducked with `sidechaincompress`.
- Word-level captions from the TTS timestamps, or transcribe the voiceover.

## Check

Before handing over, render a contact sheet (`ffmpeg -i out.mp4 -vf "fps=1,scale=270:-1,tile=4x4" -frames:v 1 sheet.jpg`) and look at it: text not cut off, nothing in the platform's bottom and right safe areas, no blank frames between scenes.
