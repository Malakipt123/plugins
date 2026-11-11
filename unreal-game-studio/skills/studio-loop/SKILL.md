---
name: studio-loop
description: Run a small game-studio loop for an Unreal Engine 5.7 project - brief, design spec, build in the editor over the UnrealClaude MCP tools, QA with logs and viewport captures, then iterate. Use when the user asks to make a game, prototype, level, mechanic or vertical slice in Unreal.
---

# Studio loop

Turn "make me a game where..." into a playable slice using the plugin's four agents.

## 0. Preflight

Call `unreal_status`. If it fails, stop and follow the `setup-unrealclaude` skill.
Call `unreal_get_project_context` to learn the project's modules, plugins and assets.

## 1. Brief (creative-director)

Delegate to `creative-director`. Get a pitch, 3 pillars, a "not now" list and acceptance criteria for the first slice. Confirm the brief with the user before building.

## 2. Spec (game-designer)

Delegate to `game-designer` for inputs, variables, a tuning table and an actor layout. Save under `Design/` in the game project.

## 3. Build (gameplay-programmer)

Delegate to `gameplay-programmer`. One system per step: build, compile, read `unreal_get_output_log`, capture the viewport.

## 4. QA (qa-tester)

Delegate to `qa-tester`. It returns a PASS / FAIL / NEEDS PLAYTEST table with evidence.

## 5. Iterate

- FAIL → back to step 3 with the bug report. Stop after 3 failed attempts on the same bug and ask the user.
- NEEDS PLAYTEST → give the user exact steps (press Play, what to try, what should happen) and wait for their result.
- All PASS → creative-director decides the next slice.

## Report to the user each round

What changed in the level and Blueprints, what passed, what needs their play test, and the next slice. Keep it short.

## Audio and faces (audio-artist)

Once the first slice plays, delegate to `audio-artist`: music per game state with the `game-music` skill (ACE-Step, local), voice lines with the `voice-lines` skill (ElevenLabs), and lip-synced faces with the `facial-animation` skill (NVIDIA Audio2Face-3D, route A). Both are local installs: get the user's approval first. The gameplay-programmer then wires the assets into Blueprints and QA checks them.
