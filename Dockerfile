FROM ghcr.io/astral-sh/uv:python3.14-alpine

ADD . /app

WORKDIR /app

RUN apk add --no-cache ffmpeg imagemagick

RUN uv sync --frozen

CMD ["uv", "run", "main.py"]