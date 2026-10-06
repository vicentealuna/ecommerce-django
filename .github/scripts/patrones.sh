#!/usr/bin/env bash
# Patrones que delatan una marca de agua de herramientas de IA.
# Los usan el hook local (.githooks/commit-msg) y la revision de GitHub.

HERRAMIENTAS='claude|anthropic|copilot|chatgpt|openai|gpt-|gemini|cursor|codex|devin|aider|windsurf|codeium|tabnine|deepseek'

# En mensajes de commit
PATRON_COMMIT="co-authored-by:.*(${HERRAMIENTAS})|(generated|created|written|generado|creado|escrito) (with|by|con|por) .*(${HERRAMIENTAS})|🤖"

# En archivos del proyecto
PATRON_CODIGO="co-authored-by:.*(${HERRAMIENTAS})|(generated|created|written|generado|creado|escrito) (with|by|con|por) .*(${HERRAMIENTAS})|noreply@anthropic\.com|claude\.com/claude-code|🤖"
