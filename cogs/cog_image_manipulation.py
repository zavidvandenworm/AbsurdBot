import traceback

from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlunparse, urlparse, urlencode
from PIL import Image, ImageEnhance, ImageChops, ImageDraw, ImageFont
from discord.ext import commands
from glitch_this import ImageGlitcher
from random import randint
from duckduckgo_search import ddg_images
from .scripts.bot_global_stuff import *
import os
import io
import asyncio
from .scripts.embeds import *
import ffmpeg


async def image_manipulation_template(ctx, image_url: str, mult: float, image_enhance_function, embed_name: str):
    r = requests.head(image_url)
    if r.headers["content-type"] not in image_formats:
        await ctx.send(embed=e_data_badimage)
        return
    download = io.BytesIO()
    store = io.BytesIO()
    try:
        download.write(requests.get(image_url).content)
        image = Image.open(download)
        image = image_enhance_function(image).enhance(float(mult))
        image.save(store, format="png")
        store.seek(0)
        await ctx.send(file=discord.File(store, filename="adjusted.png"))
    except Exception as exc:
        print(traceback.format_exc())
        embed = discord.Embed(
            title=embed_name,
            description="Something went wrong, please scream at MAB.",
            color=discord.Color.red()
        )
        if len(str(exc)) > 2000:
            exception_text = "Too long to fit in footer."
        else:
            exception_text = str(exc)
        embed.set_footer(text=f"Exception: {exception_text}")
        await ctx.send(embed=embed)


async def glitch_template(ctx, image_url, glitch_amount: float, abberation: bool = True):
    r = requests.head(image_url)
    if r.headers["content-type"] not in image_formats:
        embed = discord.Embed(
            title="Image error",
            description="The supplied url does not seem to be an image. "
                        "Was it a direct url? (ends in .png, .jpeg etc.)",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    download = io.BytesIO()
    store = io.BytesIO()
    try:
        download.write(requests.get(image_url).content)
        image = Image.open(download)
        image = ImageGlitcher().glitch_image(image, glitch_amount=glitch_amount, color_offset=abberation)
        image.save(store, format="png")
        store.seek(0)
        await ctx.send(file=discord.File(store, filename="glitch.png"))
    except Exception as exc:
        print(traceback.format_exc())
        embed = discord.Embed(
            title="Glitch",
            description="Something went wrong, please scream at MAB.",
            color=discord.Color.red()
        )
        if len(str(exc)) > 2000:
            exception_text = "Too long to fit in footer."
        else:
            exception_text = str(exc)
        embed.set_footer(text=f"Exception: {exception_text}")
        await ctx.send(embed=embed)


class ImageManipulationCommands(commands.Cog, name="Image"):
    def __init__(self):
        pass

    @commands.group(brief="A group of commands for image manipulation.")
    async def img(self, ctx):
        """
        Run this command to get an overview of all available image editing commands, such as brightness,
        contrast and more.
        """
        img_commands = {
            "brightness": "Adjust the brightness of an image.\nUsage: $img brightness <image_url> <multiplier>",
            "contrast": "Adjust the contrast of an image.\nUsage: $img contrast <image_url> <multiplier>",
            "sharpness": "Adjust the sharpness of an image.\nUsage: $img sharpness <image_url> <multiplier>",
            "saturation": "Adjust the saturation of an image.\nUsage: $img saturation <image_url> <multiplier>",
            "glitch": "Add a glitch effect to an image.\nUsage: $img glitch <image_url> <0.1-10>",
        }
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Image manipulation commands",
                description="A group of commands to edit images.",
                color=discord.Color.dark_gray()
            )
            for x, y in img_commands.items():
                embed.add_field(
                    name=x,
                    value=y,
                    inline=False
                )
            await ctx.send(embed=embed)

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
        f1.save(f"{work_dir.directory}/top{str(x)}.gif", format="GIF", append_images=frames,
                save_all=True, duration=1000, loop=0)
        await ctx.send(file=discord.File(fp=f"{work_dir.directory}/top{str(x)}.gif"))

    @commands.command(brief="Generate a top 10 list from a query, using DuckDuckGo.")
    async def top10_ddg(self, ctx, *, search_term: str):
        nw, nh = (640, 480)
        images = []

        work_dir = WorkDir()
        font = ImageFont.truetype("./data/fonts/comic.ttf", 64)

        def wtbb(text: str, out: str):
            base = Image.new("RGB", (nw, nh), color=(0, 162, 237))
            d = ImageDraw.Draw(base)
            w = d.textlength(text, font=font)
            h = 64
            d.text(((nw - w) / 1.97, (nh - h) / 1.97), text, fill=(0, 0, 0), font=font)
            d.text(((nw - w) / 2, (nh - h) / 2), text, fill=(240, 240, 240), font=font)
            base.save(out)

        # DuckDuckGo image search
        results = ddg_images(search_term, max_results=10)
        images = [r["image"] for r in results]

        x = 0
        for i in images:
            wtbb(f"number {str(x + 1)}", f"{work_dir.directory}/{str(x)}_n.png")
            loc = f"{work_dir.directory}/{str(x)}.png"
            store = io.BytesIO()
            store.write(requests.get(i).content)
            image = Image.open(store)
            image = image.resize((nw, nh))
            image.save(loc)
            x += 1

        frames = []
        wtbb(f"top {str(x)} {search_term}", f"{work_dir.directory}/cover.png")
        frames.append(Image.open(f"{work_dir.directory}/cover.png"))
        for i in range(x):
            frames.append(Image.open(f"{work_dir.directory}/{str(i)}_n.png"))
            frames.append(Image.open(f"{work_dir.directory}/{str(i)}.png"))
        f1 = frames[0]
        f1.save(f"{work_dir.directory}/top{str(x)}.gif", format="GIF", append_images=frames,
                save_all=True, duration=1000, loop=0)
        await ctx.send(file=discord.File(fp=f"{work_dir.directory}/top{str(x)}.gif"))

    @img.command(brief="Change the brightness of an image.")
    async def brightness(self, ctx, image_url: str, multiplier: float):
        """Multiplies the brightness of the given image. A multiplier of 0.5 will halve the brightness."""
        await image_manipulation_template(ctx, image_url, multiplier, ImageEnhance.Brightness, "Brightness")

    @img.command(brief="Change the contrast of an image.")
    async def contrast(self, ctx, image_url: str, multiplier: float):
        """Multiplies the contrast of the given image. A multiplier of 0.5 will halve the contrast."""
        await image_manipulation_template(ctx, image_url, multiplier, ImageEnhance.Contrast, "Contrast")

    @img.command(brief="Change the saturation of an image.")
    async def saturation(self, ctx, image_url: str, multiplier: float):
        """
        Multiplies the saturation of the given image. A multiplier of 0.5 will halve the saturation, and 0 would
        make it black and white.
        """
        await image_manipulation_template(ctx, image_url, multiplier, ImageEnhance.Color, "Saturation")

    @img.command(brief="Change the sharpness of an image.")
    async def sharpness(self, ctx, image_url: str, multiplier: float):
        """Multiplies the sharpness of the given image. A multiplier of 2 will double the sharpness."""
        await image_manipulation_template(ctx, image_url, multiplier, ImageEnhance.Sharpness, "Contrast")

    @img.command(brief="Add a glitch effect to an image.")
    async def glitch(self, ctx, image_url: str, glitch_amount: float, chromatic_abberation: bool = False):
        """Adds a glitch effect to the given image. Takes values from 0-12 (float)"""
        await glitch_template(ctx, image_url, glitch_amount, chromatic_abberation)

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
            await ctx.send(embed=e_notavideo)
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
            await ctx.send(e_invalid_generic)
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
                    await ctx.send(embed=e_invalid_generic)
                    return
                break
            print(f"waiting for audio_overlay ({str(timer)})")
            timer += 2
            await asyncio.sleep(2)
        await ctx.send(file=discord.File(fp=video_out))
        os.remove(video_dl)
        os.remove(audio_dl)
        os.remove(video_out)
