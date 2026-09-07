# A.R.I.A code graphs

These diagrams describe the current Python codebase. External libraries are shown only where they are important to the runtime flow.

## Runtime architecture

```mermaid
flowchart LR
    CLI[cli/main.py\nCLI entrypoint] --> Commands[cli/commands/info.py\nstatus, update, cache commands]
    Commands --> Linux[linux/system.py\nRAM, cache, storage]
    Commands --> Paths[config/path_config.py\npaths and JSON helpers]
    Commands --> Updater[config/updater.py\nupdate checks]

    API[server/main.py\nFastAPI server] --> Logs[Server log stream]
    API --> WebSocket[/WebSocket echo/]

    Agents[agents/nvidia.py\nNvidiaAgent] --> Loader[agents/__init__.py\nLoad_Agent]
    Loader --> ModelConfig[config/model_config.py\nprovider/model selection]
    ModelConfig --> Crypto[security/encryption/crypto.py\nAPI-key encryption]
    Crypto --> Paths
    Agents --> OpenAI[OpenAI-compatible API]

    Voice[config/voice_config.py\nvoice configuration] --> Linux
    Voice --> Paths
    Worker[workers/worker.py\nplanned worker system] --> Paths

    Paths --> Logger[logger_config.py]
    Linux --> Logger
    Commands --> Logger

    classDef entry fill:#e8f1ff,stroke:#2563eb,stroke-width:2px;
    classDef core fill:#ecfdf5,stroke:#059669,stroke-width:2px;
    classDef support fill:#fff7ed,stroke:#ea580c;
    class CLI,API,Agents entry;
    class Commands,Loader,ModelConfig,Crypto,Linux,Paths core;
    class Voice,Worker,Updater,Logger,OpenAI,Logs,WebSocket support;
```

## Internal Python import graph

```mermaid
flowchart TD
    main[main.py]
    cli[cli.main]
    info[cli.commands.info]
    internal[cli.internal]
    core[cli.internal.core.core]
    agents[agents]
    nvidia[agents.nvidia]
    model[config.model_config]
    voice[config.voice_config]
    paths[config.path_config]
    update[config.updater]
    add[config.additionals]
    crypto[security.encryption.crypto]
    errors[errors.errors]
    linux[linux.system]
    server[server.main]
    logger[logger_config]
    worker[workers.worker]

    cli --> info
    info --> paths
    info --> update
    info --> linux
    info --> logger
    core --> nvidia
    core --> model
    internal --> errors
    nvidia --> agents
    agents --> model
    agents --> errors
    model --> paths
    model --> errors
    model --> crypto
    voice --> paths
    voice --> errors
    voice --> linux
    voice --> logger
    paths --> logger
    crypto --> paths
    crypto --> errors
    linux --> logger
    linux --> server
    worker --> paths
    add --> paths
    add --> errors

    classDef cycle fill:#fee2e2,stroke:#dc2626,stroke-width:2px;
    class agents,nvidia cycle;
```

## Main execution paths

```mermaid
sequenceDiagram
    participant User
    participant CLI as cli.main
    participant Cmd as info commands
    participant Config as A.R.I.A config
    participant Linux as Linux system helper

    User->>CLI: romeo info / status / ram-info
    CLI->>Cmd: parse command and call func(args)
    alt info or status
        Cmd->>Config: read local config JSON
        Config-->>Cmd: version/status metadata
    else ram-info or cache-info
        Cmd->>Linux: show_ram_info() / show_cache_info()
        Linux-->>Cmd: system metrics
    end
    Cmd-->>User: print result
```

## Notes

- `agents` and `agents.nvidia` form an import cycle: `agents.nvidia` imports `Load_Agent` from `agents`, while `agents` owns `Load_Agent`.
- `linux.system` imports the logger object from `server.main`, which makes importing Linux initialize FastAPI server logging as a side effect.
- `main.py` is currently empty; the practical entrypoints are `cli.main`, `server.main`, and `agents.nvidia`.
