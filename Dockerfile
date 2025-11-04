FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

ADD . /app

WORKDIR /app

RUN apt update
RUN apt install --no-cache ffmpeg imagemagick

RUN uv sync

CMD ["uv", "run", "main.py"]