# Unreal Game Studio

Make Unreal Engine 5.7 games with a small agent studio that works directly in the open editor.

- **MCP server `unrealclaude`**: connects to the [UnrealClaude](https://github.com/Natfii/UnrealClaude) editor plugin (MIT) over `localhost:3000`. Tools: spawn/move/delete actors, set properties, open levels, search assets, edit Blueprints and Animation Blueprints, Enhanced Input, materials, output log and viewport capture.
- **Agents**: `creative-director` (brief and scope), `game-designer` (mechanics, tuning, layout), `gameplay-programmer` (builds it in the editor), `qa-tester` (checks acceptance criteria with logs and screenshots).
- **Skills**: `setup-unrealclaude` (install and connect), `studio-loop` (brief → spec → build → QA → iterate).
- **Rule**: `unreal-editor-safety`.

## Setup

1. Build and install UnrealClaude in your game's `Plugins/` folder and run `npm install` in `Plugins/UnrealClaude/Resources/mcp-bridge` (see the `setup-unrealclaude` skill).
2. Set the plugin variable `UNREALCLAUDE_PLUGIN_DIR` to that `Plugins/UnrealClaude` folder.
3. Open the project in Unreal Editor 5.7 and ask: "Make a small 3D platformer level with a coin to collect."

## Notes

- Requires Unreal Engine 5.7 and Node.js 18+. The editor must be open for the tools to work.
- No API keys: the bridge only talks to the local editor.
- Script execution stays hidden and permission-gated; keep "Auto-approve script execution" off.
