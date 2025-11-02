import asyncio
import enum
import glob
import os
import pathlib
import shutil
import uuid
import time

import discord
from discord.ext.commands import Context

from modules.logger import create_logger

logger = create_logger("upload module")

public_base_path = os.environ.get("PUBLIC_BASE_PATH")

if not public_base_path:
    raise Exception("Upload module: PUBLIC_BASE_PATH environment variable not set")

if not public_base_path.endswith("/"):
    public_base_path += "/"

public_folder = os.path.abspath("./public_media")

cleanup_file_interval = 600
max_file_lifespan = 24 * 60 * 60

filesize_limit_free = 10*1024*1024

if not os.path.exists(public_folder):
    os.makedirs(public_folder)

def copy_to_public(file_path: str) -> str:
    file_extension = pathlib.Path(file_path).suffix
    public_filename = f"{uuid.uuid4()}{file_extension}"
    local_path = os.path.join(public_folder, public_filename)

    shutil.copy(file_path, local_path)

    return public_filename

async def handle_upload(ctx: Context, file_path: str):
    fs = os.stat(file_path)
    file_name = pathlib.Path(file_path).name

    if fs.st_size < filesize_limit_free:
        file = discord.File(file_path, filename=file_name)
        await ctx.send(file=file)
        return

    public_filename = copy_to_public(file_path)

    await ctx.send(f"{public_base_path}file/{public_filename}")

def prune():
    global max_file_lifespan

    files = glob.glob(f"{public_folder}/*", recursive=False)

    for fp in files:
        info = os.stat(fp)
        created = info.st_mtime
        lifespan = time.time() - created
        if lifespan > max_file_lifespan:
            logger.info(f"Pruning {fp}")
            os.remove(fp)

async def prune_loop():
    global cleanup_file_interval
    logger.info("Pruner started")
    while True:
        await asyncio.sleep(cleanup_file_interval)
        prune()