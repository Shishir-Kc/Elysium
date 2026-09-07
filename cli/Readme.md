# A.R.I.A CLI

A Python-based command-line interface application for the A.R.I.A project, designed to be AI-powered and agentic.

## Current State

A.R.I.A CLI is in early development, providing a basic interactive CLI framework with a configurable model backend.

## Features

### Current Commands
- `help` - Display a help message (stub)
- `stats` - Show system information (stub)

### How It Works
1. Run the CLI - it starts an interactive prompt (`E.L >`)
2. Type a command (e.g., `help`, `stats`)
3. Input is parsed in Python and routed to the appropriate command handler

## Building & Running

```bash
python main.py
```

## Project Structure

```
cli/
├── main.py                    # Entry point
├── Config/                    # Configuration management
│   ├── cli_config.py          # CLI config with Pydantic validation & encryption
│   ├── config.json            # AI model configuration template
│   └── config.log             # Configuration operation log
├── commands/
│   ├── help/
│   │   └── help.py            # Help command (stub)
│   └── system_info/
│       └── sys_info.py        # System info command (stub)
├── internal/
│   ├── __init__.py            # Exports custom exceptions
│   ├── core/
│   │   └── core.py            # Main REPL loop & command routing
│   ├── Errors/
│   │   └── errors.py          # Custom exception classes
│   ├── parse/                 # Legacy C parser (unused)
│   │   ├── parse.c
│   │   └── parse.h
│   └── tui/                   # TUI module (pending)
└── external/                  # External integrations (empty)
```

## Dependencies

- `pydantic` - Configuration schema validation
- `requests` - HTTP requests for default config download
- `config` - Shared A.R.I.A path configuration
- `Security.encryption.crypto` - API key encryption

## Future Plans

- **AI Integration**: Route commands through configurable LLM providers (Google, OpenAI, Anthropic) for intelligent processing
- **Enhanced Commands**: Replace stub implementations with functional commands
- **External Integrations**: Populate `external/` with third-party service connectors
- **TUI Module**: Develop a terminal UI layer

## Flow 
![flow](https://raw.githubusercontent.com/Shishir-Kc/Assets/refs/heads/main/Elysium_cli/flow.png)

## License

[To be determined]
