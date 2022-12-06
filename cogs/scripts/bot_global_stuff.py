import os.path

from glob import glob
import random
import shutil
from pathlib import Path

import inspect
import subprocess


import sys
import requests
import time
import mimetypes

from pydub import AudioSegment

image_formats = ["image/png", "image/jpeg", "image/jpg", "image/tiff"]

audio_formats = ["audio/mpeg", "audio/wav", "audio/x-wav", "audio/ogg"]

formats = {
    "audio/mpeg": "mp3",
    "audio/x-wav": "wav",
    "audio/wav": "wav",
    "audio/ogg": "ogg"
}

bcg_soundpacks = {
    "default": None
}

drummachine_library = {}

for i in glob(r"./data/samples/drum_machine/*.wav"):
    drummachine_library[Path(i).stem] = os.path.abspath(i)


def http_is_av(url: str):
    headers = requests.head(url).headers
    if not any(ext in headers["content-type"] for ext in ["audio", "video"]) and \
        headers['content-type'] != "application/x-shockwave-flash":
        return False
    else:
        return True


def http_is_img(url: str, strict: bool = False):
    headers = requests.head(url).headers
    if strict:
        if not any(headers["content-type"] == ext for ext in image_formats):
            return False
    else:
        if "image" not in headers['content-type'] or headers['content-type'] == "image/gif":
            return False
    return True


def http_is_audio(url: str):
    headers = requests.head(url).headers
    if not any(headers["content-type"] == ext for ext in audio_formats):
        return False
    else:
        return True


def http_is_video(url: str):
    headers = requests.head(url).headers
    if "video" not in headers['content-type'] and headers['content-type'] != "image/gif" and headers['content-type']\
            != "application/x-shockwave-flash":
        return False
    else:
        return True


def http_has_frames(url: str):
    headers = requests.head(url).headers
    if "video" not in headers['content-type']\
            and "audio" not in headers['content-type']\
            and headers['content-type'] != "application/x-shockwave-flash"\
            and headers['content-type'] != "image/gif":
        return False
    else:
        return True


def media_require(url, media_type: str, gohere=os.path.abspath("./temp")):
    uid = str(int(time.time_ns()))
    location_directory = gohere
    if media_type == "audio":
        if not http_is_audio(url):
            return False
    if media_type == "video":
        if not http_is_video(url):
            return False
    if media_type == "audiovideo":
        if not http_is_av(url):
            return False
    if media_type == "image":
        if not http_is_img(url):
            return False
    if media_type == "imagevideo":
        if not http_is_img(url) and not http_is_video(url):
            return False
    if media_type == "frames":
        if not http_has_frames(url):
            return False
    request_data = requests.get(url).content
    ext = mimetypes.guess_extension(requests.head(url).headers['content-type'].partition(';')[0].strip())
    location = f"{location_directory}/{uid}_{str(time.time_ns())}{ext}"
    print(location)
    with open(location, "wb") as f:
        f.write(request_data)
    return location


def url2ext(url):
    ext = mimetypes.guess_extension(requests.head(url).headers['content-type'].partition(';')[0].strip())
    return ext[1:]


class WorkDir:
    def __init__(self):
        base = os.path.abspath("./data/temp")
        if not os.path.exists(base):
            os.mkdir(base)
        self.directory = os.path.abspath(os.path.normpath(f"{base}/{str(time.time_ns())}"))
        os.mkdir(self.directory)

    def __del__(self):
        if os.path.exists(self.directory):
            shutil.rmtree(self.directory)


def speed_change(sound, speed=1.0, framerate: int = None):
    sound_altered = sound._spawn(sound.raw_data, overrides={
        "frame_rate": (int(sound.frame_rate * speed)) if framerate is None else framerate
    })
    return sound_altered.set_frame_rate(sound.frame_rate)


def func2subpr(func, **kwargs):
    work_dir = WorkDir()
    code_loc = f"{work_dir.directory}/code.py"
    source = ""
    for mod in sys.modules:
        source += f"import {str(mod)}\n"
    for kw, arg in kwargs.items():
        source += f"{str(kw)} = {str(arg)}\n"
    source += inspect.getsource(func)
    source += f"\n{func.__name__}()"
    print(source)
    with open(code_loc, "w") as f:
        f.write(source)
    subprocess.Popen(["python3", code_loc], shell=False, cwd=os.path.dirname(os.path.realpath(__file__)))
