import discord
import asyncio
from discord.ext import commands

from cogs.cog_artificial_intelligence import ArtificialIntelligenceCommands
from cogs.cog_audio_manipulation import AudioManipulationCommands
from cogs.cog_image_manipulation import ImageManipulationCommands
from cogs.cog_internet_stuff import InternetCommands
from cogs.cog_generic import GenericCog

from cogs.scripts.service_setup import discord_token

intents = discord.Intents().default()
intents.members = True
intents.message_content = True

prefix = "-"

activity = discord.Activity(
    type=discord.ActivityType.listening,
    name=f"{prefix}help",
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
        await bot.add_cog(InternetCommands())
        await bot.add_cog(ImageManipulationCommands())
        await bot.add_cog(ArtificialIntelligenceCommands())
        await bot.add_cog(AudioManipulationCommands())
        await bot.start(discord_token)

asyncio.run(main())
