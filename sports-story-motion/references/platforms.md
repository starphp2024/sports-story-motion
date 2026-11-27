# Platform adapters (checked 2026-11-27)

A skill is instructions plus scripts/assets, not an independent video service. Probe the actual host.

| Surface | Package | Requirements |
|---|---|---|
| Claude chat/web/desktop chat | Claude-Skill ZIP via Customize > Skills | Code execution enabled; may lack Node/Chromium/network or AI Studio browser access. Export project and render locally if unavailable. |
| Claude Code CLI / desktop Code local session | Claude-Code plugin; .claude-plugin/plugin.json + skills/ | Terminal, Python, Node, Chromium, FFmpeg; AI Studio access separately available. |
| Codex CLI / desktop | Portable root plugin.json, .codex-plugin fallback, .agents/plugins/marketplace.json | Local tools subject to host permissions; installation does not grant account/browser access. |
| Antigravity App / CLI / IDE | .antigravity-plugin/plugin.json + skills/ | Each surface discovers plugins per docs; external runtime/audio tools still require probing. |

Distinguish shell commands from in-chat slash commands. Recheck docs when client versions differ.

- [Claude skill ZIP upload](https://support.claude.com/en/articles/12512180-use-skills-in-claude)
- [Claude Code manifest](https://code.claude.com/docs/en/plugins/manifest-reference)
- [Claude Code install](https://code.claude.com/docs/en/plugins/install)
- [Codex structure](https://developers.openai.com/plugins/build/plugins)
- [Codex CLI](https://learn.chatgpt.com/docs/cli/reference)
- [Antigravity plugins](https://antigravity.google/docs/plugins)
- [Antigravity validation](https://antigravity.google/docs/build-plugins)
- [Antigravity discovery](https://antigravity.google/docs/skills)

Runtime status is separate from documentation compatibility. No OAuth server, keys or account access is bundled.
