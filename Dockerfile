FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libsndfile1 libatomic1 ffmpeg && \
    rm -rf /var/lib/apt/lists/*

RUN uv sync

COPY . .

CMD ["uv", "run", "main.py"]