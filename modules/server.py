import os
import mimetypes
from pathlib import Path
from typing import BinaryIO, Tuple, Generator

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import StreamingResponse, Response

PUBLIC_FOLDER = Path("./public_media").resolve()


def _safe_path(path: str) -> Path:
    """Prevent path traversal (../../etc/passwd)"""
    resolved = (PUBLIC_FOLDER / path).resolve()
    if not str(resolved).startswith(str(PUBLIC_FOLDER)):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")
    return resolved


def _parse_range(range_header: str, file_size: int) -> Tuple[int, int]:
    try:
        byte_range = range_header.replace("bytes=", "").split("-")
        start = int(byte_range[0]) if byte_range[0] else 0
        end = int(byte_range[1]) if byte_range[1] else file_size - 1
    except ValueError:
        raise HTTPException(status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

    if start > end or start < 0 or end > file_size - 1:
        raise HTTPException(status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

    return start, end


def _file_stream(file_obj: BinaryIO, start: int, end: int, chunk_size: int = 64_000) -> Generator[bytes, None, None]:
    try:
        file_obj.seek(start)
        remaining = end - start + 1
        while remaining > 0:
            read_size = min(chunk_size, remaining)
            data = file_obj.read(read_size)
            if not data:
                break
            remaining -= len(data)
            yield data
    finally:
        file_obj.close()


def serve_range_file(request: Request, filepath: Path) -> StreamingResponse:
    if not filepath.exists() or not filepath.is_file():
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    file_size = filepath.stat().st_size
    range_header = request.headers.get("range")

    content_type = mimetypes.guess_type(str(filepath))[0] or "application/octet-stream"
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Type": content_type,
        "Cache-Control": "public, max-age=31536000, immutable"
    }

    start = 0
    end = file_size - 1
    status_code = status.HTTP_200_OK

    if range_header:
        start, end = _parse_range(range_header, file_size)
        size = end - start + 1
        headers["Content-Length"] = str(size)
        headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        status_code = status.HTTP_206_PARTIAL_CONTENT
    else:
        headers["Content-Length"] = str(file_size)

    file_obj = open(filepath, "rb")
    return StreamingResponse(
        _file_stream(file_obj, start, end),
        headers=headers,
        status_code=status_code,
    )


app = FastAPI()


@app.get("/file/{file_path:path}")
async def serve_file(request: Request, file_path: str):
    filepath = _safe_path(file_path)
    return serve_range_file(request, filepath)


async def start_uvicorn():
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=3000,
        log_level="info",
        lifespan="off"
    )
    server = uvicorn.Server(config)
    await server.serve()