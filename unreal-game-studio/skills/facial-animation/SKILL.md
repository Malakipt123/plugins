---
name: facial-animation
description: Make Unreal characters talk with lip-sync and facial expression generated from voice audio using NVIDIA Audio2Face-3D (ACE). Use when the user wants an NPC or MetaHuman to speak dialogue, needs lip-sync, or asks for animated faces in their game.
---

# Facial animation with NVIDIA Audio2Face-3D

[Audio2Face-3D](https://github.com/NVIDIA/Audio2Face-3D) turns a voice line (WAV) into facial animation: lip-sync, jaw, tongue, eyes and emotion inferred from the tone. It ships as an Unreal Engine plugin (MIT source) plus model plugins (NVIDIA Open Model License; Audio2Emotion models may only be used with Audio2Face).

## Important: engine version

The NVIDIA ACE Unreal plugin is published for **UE 5.4, 5.5 and 5.6**, while UnrealClaude needs **UE 5.7**. Before starting, check NVIDIA's [Audio2Face-3D page](https://github.com/NVIDIA/Audio2Face-3D#audio2face-3d-unreal-engine-5-plugin) for a 5.7 build. If there is none, use one of these routes and tell the user which one:

| Route | How | Good for |
|---|---|---|
| **A. Bake in 5.6, use in 5.7** | Keep a small UE 5.6 "face lab" project with the ACE plugin. Generate the animation there, bake it to an Animation Sequence on the same face skeleton, then **Asset Actions → Migrate** it into the 5.7 game project. | Pre-written dialogue and cutscenes |
| **B. Maya ACE → FBX** | Use [Maya-ACE](https://github.com/NVIDIA/Maya-ACE) to generate blendshape/joint animation and export FBX, then import into 5.7. | Teams that already use Maya |
| **C. Runtime in 5.6** | Build the game on 5.6 with the ACE plugin for live, in-game lip-sync (UnrealClaude tools will not be available in that project). | Dynamic dialogue generated at runtime |

## Requirements

- NVIDIA RTX GPU for local inference (there is a CPU fallback in the SDK, much slower). Remote inference through the Audio2Face-3D NIM needs an NVIDIA API key: keep it in an environment variable or the editor's settings, never in project files or this plugin.
- A character with a face rig: MetaHuman works out of the box with the sample mappings; custom faces need ARKit-style blendshapes or a mapping.

## Setup (route A or C, user runs it)

1. Download from NVIDIA (links on the Audio2Face-3D page): the **ACE Unreal plugin** for the engine version, the **Audio2Face-3D 3.0 models plugin**, and optionally the **Unreal sample project** (MetaHuman setup to copy from).
2. Unzip both plugins into `<Project>/Plugins/`, open the project and enable them.
3. Copy the character setup from the sample project: the ACE component on the face and the Anim Blueprint that applies its curves to the rig. Read the exact component and node names there instead of guessing.

## Make a character talk

1. Get the voice line as WAV (16 kHz+ mono is fine): a recording, or TTS. The `grok-voice` plugin in this marketplace can produce read-aloud audio; any TTS the user already pays for also works.
2. Import the WAV into Unreal as a Sound Wave.
3. In Blueprint, call the ACE node that animates a character from a Sound Wave (find it with `unreal_ue` → `blueprint` → `search_nodes`, or in the sample project).
4. For route A, record the result with Take Recorder or the plugin's bake option to an Animation Sequence, then migrate it.
5. QA: `unreal_capture_viewport` mid-line and listen in PIE. Check that mouth closes on M/B/P sounds and that emotion fits the line.

## Do not

- Do not download or install NVIDIA plugins or models without the user's OK; they are large and carry their own licenses.
- Do not invent ACE node or component names in instructions: read them from the installed plugin or sample project.
