import discord
import asyncio
from discord.ext import commands

from cogs.cog_audio_manipulation import AudioManipulationCommands
from cogs.cog_image_manipulation import ImageManipulationCommands
from cogs.cog_internet_stuff import InternetCommands
from cogs.cog_generic import GenericCog
from os import environ

from cogs.cog_nice_stuff import NiceCommands

TOKEN = environ["DISCORD_TOKEN"]

if TOKEN == "":
    raise Exception("DISCORD_TOKEN environment variable not set")

intents = discord.Intents().default()
intents.members = True
intents.message_content = True

prefix = environ["BOT_PREFIX"] or "$"

activity = discord.Activity(
    type=discord.ActivityType.listening,
    name=f"{prefix}help - hello haii",
    intents=intents
)

bot = commands.Bot(
    command_prefix=prefix,
    activity=activity,
    intents=intents
)


async def main():
    async with bot:
        await bot.add_cog(GenericCog())
        await bot.add_cog((NiceCommands()))
        await bot.add_cog(InternetCommands())
        await bot.add_cog(ImageManipulationCommands())
        await bot.add_cog(AudioManipulationCommands())
        await bot.start(TOKEN)

asyncio.run(main())
