import logging

import discord
import asyncio
from discord.ext import commands

from cogs.cog_audio_manipulation import AudioManipulationCommands
from cogs.cog_image_manipulation import ImageManipulationCommands
from cogs.cog_internet_stuff import InternetCommands
from cogs.cog_generic import GenericCog
from os import environ

from cogs.cog_nice_stuff import NiceCommands
from modules.logger import create_logger
from modules.server import start_uvicorn

logger = create_logger('bot main')
logger.setLevel(logging.DEBUG)

def create_bot():
    intents = discord.Intents().all()

    env_prefix = environ.get('BOT_PREFIX')

    if env_prefix:
        prefix = env_prefix
    else:
        logger.warn('BOT_PREFIX not set, defaulting to $')
        prefix = '$'

    activity = discord.Activity(
        type=discord.ActivityType.listening,
        name=f"{prefix}help - hello",
        intents=intents
    )

    bot = commands.Bot(
        command_prefix=prefix,
        activity=activity,
        intents=intents
    )

    return bot

async def start_bot():
    token = environ.get("DISCORD_TOKEN")

    if not token:
        raise Exception("DISCORD_TOKEN environment variable not set")

    bot = create_bot()

    @bot.event
    async def on_ready():
        logger.info("absurd is ONLINE")
        asyncio.create_task(start_uvicorn())

    async with bot:
        await bot.add_cog(GenericCog(bot))
        await bot.add_cog((NiceCommands()))
        await bot.add_cog(InternetCommands())
        await bot.add_cog(ImageManipulationCommands(bot))
        await bot.add_cog(AudioManipulationCommands())

        await bot.start(token)

def main():
    asyncio.run(start_bot())


if __name__ == "__main__":
    main()