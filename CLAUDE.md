# CLAUDE.md

Fork of the Cursor plugin marketplace. Each plugin is a standalone directory
(first-party at the root, third-party MCP integrations under `third_party/`)
with its own `.cursor-plugin/plugin.json`. The root
`.cursor-plugin/marketplace.json` lists every plugin.

## Map

- `.cursor-plugin/marketplace.json` – marketplace index (`name`, `source`, `description` per plugin).
- `<plugin>/.cursor-plugin/plugin.json` – manifest; schema in `schemas/plugin.schema.json`.
- `<plugin>/skills/<skill>/SKILL.md` – agent skills with `name` + `description` frontmatter.
- `<plugin>/rules/*.mdc` – Cursor rules (`description`, `alwaysApply` frontmatter).
- `<plugin>/agents/`, `<plugin>/hooks/hooks.json`, `<plugin>/mcp.json` – subagents, hooks, MCP servers.
- `third_party/<name>/` – usually just `plugin.json`, `mcp.json`, `README.md`, `CHANGELOG.md`, `assets/logo.png`.
- `create-plugin/` – the plugin that scaffolds new plugins; follow its conventions.
- `grok-voice/` – Grok realtime voice, dictation, read-aloud and debug skills (related to Jarvis in `grok-bot-0.18-reconstructed`).

To understand one plugin, read its `plugin.json` and `README.md` first; most
of the repo is markdown, so open only the skill you need.

## Adding or changing a plugin

1. Create or edit `<plugin>/.cursor-plugin/plugin.json` (`name` must match the directory's marketplace entry).
2. Add or update its entry in `.cursor-plugin/marketplace.json`.
3. Add a row to the table in the root `README.md`.
4. Bump `version` in `plugin.json` and note the change in the plugin's `CHANGELOG.md` when one exists.

## Validation

```sh
npm install --no-save ajv ajv-formats
node scripts/validate-plugins.mjs
```

CI (`.github/workflows/validate-plugins.yml`, Node 20) runs the same check on
pull requests that touch manifests or schemas. It verifies both schemas, that
each `source` directory and `plugin.json` exist, and that marketplace and
manifest names match.

## Rules

- Never put API keys or tokens in `mcp.json` or skills; reference environment variables or OAuth.
- Keep skill `description` fields specific: they decide when an agent loads the skill.
