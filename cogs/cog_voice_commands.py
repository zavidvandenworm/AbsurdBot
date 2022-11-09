from discord.ext import commands
from .scripts.bot_global_stuff import *
from .scripts.embeds import *

class VoiceChatCommands(commands.Cog, name="Voice Chat"):
    def __init__(self):
        pass

    @commands.group(brief="A bunch of VC related commands")
    async def vc(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=i_vc)
            return

    @vc.command(brief="Play an audio file in the voice chat.")
    async def file_play(self, ctx, audio_url):
        work_dir = WorkDir()
        audio_local = media_require(audio_url, "audio", work_dir.directory)
        if audio_local is None:
            await ctx.send(embed=e_invalid_generic)
            return
