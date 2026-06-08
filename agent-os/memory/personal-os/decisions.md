# Decisions

- Use `AGENTS.md` instead of `CLAUDE.md` because the target stack is Gemini/VS Code rather than Claude/Cowork.
- Use direct Gemini API calls for production rather than Gemini CLI because API calls are easier to secure, log, and constrain.
- Use local files as source of truth before introducing databases or external connectors.
