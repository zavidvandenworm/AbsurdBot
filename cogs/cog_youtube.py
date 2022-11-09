import io

from discord.ext import commands
import random
from pytube import YouTube
from .scripts.embeds import *
from pydub import AudioSegment
import requests
from .extra.proxy_list import prox


class YoutubeCommands(commands.Cog):
    def __init__(self):
        pass

    @commands.command()
    async def yt2mp3(self, ctx, youtube_link):
        store = io.BytesIO()
        converted = io.BytesIO()
        proxy_choice = random.choice(prox)
        yt = YouTube(youtube_link, proxies=proxy_choice)
        yt_audio = yt.streams.filter(only_audio=True).first()
        if yt_audio.filesize > 8388608:
            await ctx.send(embed=embeds.e_youtube_toobig)
            return
        store.write(requests.get(yt_audio.url).content)
        store.seek(0)
        conv = AudioSegment.from_file(store)
        conv.export(converted, format="mp3")
        await ctx.send(file=discord.File(fp=converted, filename="yt2.mp3"))
