from discord.ext import commands
from .scripts.bot_global_stuff import *
from .scripts.embeds import *



class AbsurdDaw(commands.Cog, name="AbsurdDAW"):
    def __init__(self):
        pass

    @commands.command(brief="Start an AbsurdDAW session")
    async def daw(self, ctx, audio_url):
        work_dir = WorkDir()
        audio_local = media_require(audio_url, "audio", work_dir.directory)
        if audio_local is None:
            await ctx.send(embed=e_daw_audio)
            return
