import pathlib
import random
import tempfile
import traceback

import discord.ui
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlunparse, urlparse, urlencode
from PIL import Image, ImageEnhance, ImageChops, ImageDraw, ImageFont
from discord import Interaction
from discord._types import ClientT
from discord.ext import commands
from glitch_this import ImageGlitcher

from random import randint

from modules.automodal import automodal
from modules.image import adjust_image
from modules.logger import create_logger
from modules.regex_patterns import URL_RE
from modules.web_file import WebFile, WebFileTypes
from .scripts.bot_global_stuff import *
import os
import io
import asyncio
import ffmpeg

logger = create_logger("image cog")


async def handle_image_edit_modal(interaction: discord.Interaction, brightness, contrast, sharpness):
    print(brightness, contrast, sharpness)

    web_file = WebFile(self.image_url_input.value)

    if not web_file.fetch(WebFileTypes.IMAGE):
        await interaction.response.send_message("Your image did not pass the filetype check.", ephemeral=True)
        return

    with tempfile.TemporaryDirectory() as tmpdirname:
        path = web_file.save(tmpdirname)
        p = pathlib.Path(path)
        out_path = f"{p.parent}/process_{p.name}"

        edit_success = adjust_image(
            path,
            out_path,
            brightness=brightness,
            contrast=contrast,
            sharpness=sharpness
        )

        if not edit_success:
            await interaction.response.send_message("Edit failed.", ephemeral=True)
            return

        logger.info("edited file")

        file_upload = discord.File(fp=out_path, filename=f"process_{p.name}")

        await interaction.user.send(file=file_upload)


class ImageEditorView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @discord.ui.button(label="Edit image", style=discord.ButtonStyle.primary)
    async def run_editor(self, interaction: discord.Interaction, button: discord.ui.Button):
        edit_modal = automodal("absurdGIMP", {
            "image_url": {
                "type": "url",
                "label": "Brightness (-100 to 100)",
                "placeholder": 0,
                "required": True,
                "default": 0
            },
            "brightness": {
                "type": "number",
                "label": "Brightness (-100 to 100)",
                "placeholder": 0,
                "required": False,
                "default": 0
            },
            "contrast": {
                "type": "number",
                "label": "Contrast (-100 to 100)",
                "placeholder": 0,
                "required": False,
                "default": 0
            },
            "sharpness": {
                "type": "number",
                "label": "Sharpness (-100 to 100)",
                "placeholder": 0,
                "required": False,
                "default": 0
            }
        }, handle_image_edit_modal)

        await interaction.response.send_modal(edit_modal)


class ImageManipulationCommands(commands.Cog, name="Image"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        pass

    @commands.command(brief="Image editor.")
    async def editor(self, ctx: commands.Context):
        await ctx.send(view=ImageEditorView(bot=self.bot))

    @commands.command(brief="Generate a top 10 list from a search term(s).")
    async def top10(self, ctx, *, search_term: str):
        image_amount = 999

        nw, nh = (640, 480)
        images = []

        work_dir = WorkDir()

        font = ImageFont.truetype("./data/fonts/comic.ttf", 64)

        search_encoded = urlencode({"q": search_term, "amount": image_amount})

        def wtbb(text: str, out: str):
            base = Image.new("RGB", (nw, nh), color=(0, 162, 237))
            d = ImageDraw.Draw(base)
            w = d.textlength(text, font=font)
            h = 64
            d.text(((nw - w) / 1.97, (nh - h) / 1.97), text, fill=(0, 0, 0), font=font)
            d.text(((nw - w) / 2, (nh - h) / 2), text, fill=(240, 240, 240), font=font)
            base.save(out)

        def make_request(url):
            r = requests.get(url)
            return r.content.decode("utf-8")

        search_link = f"https://www.bing.com/images/search?{search_encoded}"
        htmldata = make_request(search_link)
        soup = BeautifulSoup(htmldata, 'html.parser')
        for item in soup.find_all('img', {"class": "mimg"}):
            try:
                u = urlparse(item["src"])
                query = parse_qs(u.query, keep_blank_values=False)
                query.clear()
                u = u._replace(query=urlencode(query, True))
                u = urlunparse(u)
                images.append(u)
            except:
                pass
        x = 0
        for i in images:
            wtbb(f"number {str(x + 1)}", f"{work_dir.directory}/{str(x)}_n.png")
            loc = f"{work_dir.directory}/{str(x)}.png"
            store = io.BytesIO()
            store.write(requests.get(i).content)
            image = Image.open(store)
            image = image.resize((nw, nh))
            image = image.save(loc)
            x += 1

        frames = []
        wtbb(f"top {str(x)} {search_term}", f"{work_dir.directory}/cover.png")
        frames.append(Image.open(f"{work_dir.directory}/cover.png"))
        for i in range(0, x):
            frames.append(Image.open(f"{work_dir.directory}/{str(i)}_n.png"))
            frames.append(Image.open(f"{work_dir.directory}/{str(i)}.png"))
        f1 = frames[0]

        gif_fp = f"{work_dir.directory}/top{str(x)}.gif"
        mp4_fp = f"{work_dir.directory}/top{str(x)}.mp4"

        f1.save(gif_fp, format="GIF", append_images=frames,
                save_all=True, duration=1000, loop=0)

        input_gif = ffmpeg.input(gif_fp)
        input_music = ffmpeg.input(f"./data/samples/top10/{random.randint(1, 13)}.mp3")

        ffmpeg.concat(input_gif, input_music, v=1, a=1).output(mp4_fp).run()

        await ctx.send(file=discord.File(fp=mp4_fp))

    @commands.command(brief="Turn your image into a cover!")
    async def covergen(self, ctx, url):
        r = requests.head(url)
        if r.headers["content-type"] in image_formats:
            store = io.BytesIO()
            fn = f"{str(ctx.author.id)}-temp.png"
            open(fn, "wb").write(requests.get(url).content)
            img = Image.open(fn)
            rave = Image.open("./data/covergen/rave.png")
            img = ImageEnhance.Contrast(img).enhance(0.1 * randint(13, 22))
            img = ImageEnhance.Sharpness(img).enhance(0.1 * randint(13, 22))
            rave = ImageEnhance.Sharpness(img).enhance(1)
            rave = rave.resize(img.size)
            rave = ImageChops.invert(rave)
            rave = ImageEnhance.Contrast(rave).enhance(.1 * randint(5, 30))
            img = ImageEnhance.Color(img).enhance(.1 * randint(1, 10))
            img = ImageChops.subtract_modulo(img, rave)
            img = ImageGlitcher().glitch_image(img, glitch_amount=randint(2, 5), color_offset=True).save(
                store, format="png")
            store.seek(0)
            await ctx.send(file=discord.File(fp=store, filename="process.png"))
            store.close()
            os.remove(fn)
        else:
            embed = discord.Embed(
                title="Bad Image",
                description="Supplied image is not supported!"
            )
            await ctx.send(embed=embed)

    @commands.command(brief="Convert any video or gif into a mp4")
    async def any2mp4(self, ctx, any_url, *kwargs):
        work_dir = WorkDir()
        mp4_path = f"{work_dir.directory}/any2mp4.mp4"
        local_path = media_require(any_url, "audiovideo", work_dir.directory)
        if local_path is None:
            await ctx.send("Not a video")
        with open(local_path, "wb") as f:
            f.write(requests.get(any_url).content)
        (
            ffmpeg
            .input(local_path)
            .output(mp4_path)
            .run()
        )
        await ctx.send(file=discord.File(fp=mp4_path))

    @commands.command(brief="Overlay audio over a video or image.")
    async def audio_overlay(self, ctx, image_video_url, audio_url, *kwargs):
        work_dir = WorkDir()
        if "lq" in kwargs:
            bitrate = 500
        else:
            bitrate = 10000
        imgtest = http_is_img(image_video_url)
        video_dl = media_require(image_video_url, "imagevideo")
        audio_dl = media_require(audio_url, "audio")
        video_out = os.path.abspath(f"{work_dir.directory}/av-overlay-out.mp4")
        if video_dl is None or audio_dl is None:
            await ctx.send("Invalid files")
            return
        p = subprocess.Popen(["python3", "audio_overlay.py", str(ctx.author.id), str(video_dl), str(audio_dl),
                              str(bitrate), str(kwargs), str(imgtest), str(video_out)],
                             shell=False, cwd=os.path.dirname(os.path.realpath(__file__)))
        timer = 0
        while True:
            if p.poll() is not None:
                print(f"completed, with exit code {str(p.poll())}")
                if p.poll() != 0:
                    print("failed to execute audio_overlay!")
                    await ctx.send(embed="Generic error")
                    return
                break
            print(f"waiting for audio_overlay ({str(timer)})")
            timer += 2
            await asyncio.sleep(2)
        await ctx.send(file=discord.File(fp=video_out))
        os.remove(video_dl)
        os.remove(audio_dl)
        os.remove(video_out)
