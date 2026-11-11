---
name: setup-unrealclaude
description: Install and connect the UnrealClaude editor plugin (Natfii/UnrealClaude) to Unreal Engine 5.7 so agents can drive the editor over MCP. Use when unreal_status fails, the unrealclaude MCP server is missing, or the user starts a new Unreal game project.
---

# Set up UnrealClaude

UnrealClaude is an MIT-licensed Unreal Engine 5.7 editor plugin. It runs an HTTP server inside the editor on `localhost:3000`; a Node MCP bridge in `Resources/mcp-bridge` turns that into MCP tools named `unreal_*`. Nothing leaves the machine except your normal model traffic.

## Requirements

- Unreal Engine **5.7** (Windows, Linux or Apple Silicon macOS) and a C++ toolchain to build plugins (Visual Studio 2022 on Windows, Xcode on macOS).
- Node.js 18+.

## Steps (walk the user through them; they run on their machine)

1. Clone with the bridge submodule:
   ```sh
   git clone --recurse-submodules https://github.com/Natfii/UnrealClaude.git
   ```
2. Build for the engine (Windows example):
   ```bat
   "C:\Program Files\Epic Games\UE_5.7\Engine\Build\BatchFiles\RunUAT.bat" BuildPlugin -Plugin="C:\src\UnrealClaude\UnrealClaude\UnrealClaude.uplugin" -Package="C:\src\UnrealClaude-Build" -TargetPlatforms=Win64
   ```
   macOS/Linux use `Engine/Build/BatchFiles/RunUAT.sh` with `-TargetPlatforms=Mac` or `Linux`.
3. Copy the build output to `<YourGame>/Plugins/UnrealClaude/`.
4. Install the bridge dependencies:
   ```sh
   cd <YourGame>/Plugins/UnrealClaude/Resources/mcp-bridge
   npm install
   ```
5. Open the project in the editor. The Output Log should show `MCP Server started on http://localhost:3000`.
6. Check it: `curl http://localhost:3000/mcp/status` returns JSON with the project name.
7. Set this plugin's `UNREALCLAUDE_PLUGIN_DIR` variable to `<YourGame>/Plugins/UnrealClaude` (forward slashes are fine on Windows), then reload MCP servers. Call `unreal_status` to confirm.

## Safety

- Leave **Project Settings → Plugins → Unreal Claude → Auto-approve script execution** OFF. Script tools stay hidden from the model by design; `run_console_command` can reach Python.
- Review the plugin source before building it, as with any editor plugin: it runs inside your editor with your user's permissions.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `unreal_*` tools missing | `npm install` in `Resources/mcp-bridge`, check `UNREALCLAUDE_PLUGIN_DIR`, reload MCP |
| `unreal_status` says not connected | Editor closed, or port 3000 busy: look for `LogUnrealClaude` in the Output Log |
| Plugin fails to compile | Engine is not 5.7, or the C++ toolchain is missing |
| Requests hang | Project on OneDrive/Dropbox: move it to a local folder |
