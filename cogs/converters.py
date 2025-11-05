import tempfile

import discord
from discord.ext import commands

from modules.audio import convert_to_mp3, convert_to_mp4
from modules.jobs import TaskManager
from modules.upload import handle_upload
from modules.web_file import WebFile


class ConverterCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.task_manager = TaskManager()
        self.bot = bot

    @commands.command(brief="Convert any audio/video file into a mp3!")
    async def tomp3(self, ctx, audio_url):
        """
        Takes a direct link to any audio or video file as an argument, and converts it to mp3.
        """
        with tempfile.TemporaryDirectory() as tmpdirname:
            dl = WebFile(audio_url)
            if not dl.check():
                return await ctx.send("Failed to download file.")
            fp = dl.save(tmpdirname)

            out_path = f"{tmpdirname}/convert.mp3"

            job = await self.task_manager.run(convert_to_mp3, fp, out_path)

            if not job.success:
                return await ctx.send("Conversion failed.")

            await handle_upload(ctx, out_path)

    @commands.command(brief="Convert any audio/video file into a mp3!")
    async def tomp4(self, ctx, audio_url):
        """
        Takes a direct link to any audio or video file as an argument, and converts it to mp4.
        """
        with tempfile.TemporaryDirectory() as tmpdirname:
            dl = WebFile(audio_url)
            if not dl.check():
                return await ctx.send("Failed to download file.")
            fp = dl.save(tmpdirname)

            out_path = f"{tmpdirname}/convert.mp4"

            job = await self.task_manager.run(convert_to_mp4, fp, out_path)

            if not job.success:
                return await ctx.send("Conversion failed.")

            await handle_upload(ctx, out_path)