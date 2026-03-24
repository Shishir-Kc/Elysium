FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN apt-get update && apt-get install -y build-essential portaudio19-dev python3-dev && rm -rf /var/lib/apt/lists/*

RUN uv sync --frozen --no-dev

COPY . . 

EXPOSE 8000

CMD ["/app/.venv/bin/python", "-m", "uvicorn", "main:elysium_server", "--host", "0.0.0.0", "--port", "8000"]
