import os
import time
import mimetypes
import requests
import filetype
from enum import Enum
from urllib.parse import urlparse
from pathlib import Path

from modules.logger import create_logger

logger = create_logger('web file')

class WebFileTypes(Enum):
    IMAGE = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    VIDEO = ["video/mp4", "video/webm", "video/quicktime"]
    AUDIO = ["audio/mpeg", "audio/wav", "audio/ogg"]
    FLASH = ["application/x-shockwave-flash"]
    OTHER = []

class WebFile:
    def __init__(self, url: str):
        self.url = url
        self.filename = Path(urlparse(url).path).name or "unknown"
        self.extension = Path(self.filename).suffix.lower().lstrip(".") or None
        self.mime = None
        self.type = None
        self.data = None

    def head(self):
        resp = requests.head(self.url, timeout=10, allow_redirects=True)
        resp.raise_for_status()
        return resp.headers

    def detect_type(self, headers=None):
        headers = headers or self.head()
        ctype = headers.get("content-type", "").split(";")[0]
        self.mime = ctype
        for t in WebFileTypes:
            if ctype in t.value or any(ctype.startswith(x.split("/")[0]) for x in t.value):
                self.type = t
                break
        return self.type

    def fetch(self, allowed_type: WebFileTypes | None = None) -> bool:
        headers = self.head()
        self.detect_type(headers)

        if allowed_type and self.type != allowed_type:
            logger.warn(f"File has mimetype ({self.mime}) but expected {allowed_type.name.lower()}. (From url: {self.url})")
            return False

        resp = requests.get(self.url, timeout=15)
        resp.raise_for_status()
        self.data = resp.content

        kind = filetype.guess(self.data[:262])
        if kind:
            self.mime = kind.mime
            if allowed_type and self.mime not in allowed_type.value:
                logger.warn(f"File did not pass filetype check. (From url: {self.url})")
                return False
            self.extension = kind.extension or self.extension
        return True

    def save(self, to: str) -> str:
        if not self.data:
            raise ValueError(f"File at {self.url} has no data.")
        os.makedirs(to, exist_ok=True)
        uid = str(int(time.time_ns()))
        ext = f".{self.extension}" if self.extension else mimetypes.guess_extension(self.mime) or ""
        path = os.path.join(to, f"{uid}{ext}")
        with open(path, "wb") as f:
            f.write(self.data)
            print(len(self.data))
        return path