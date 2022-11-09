import random
import traceback

import discord
import requests
from discord.ext import commands
from random import randint
from .scripts.service_setup import reddit, aw_tnadne


async def reddit_random_template(ctx, subreddit_name: str, embed_title: str):
    sub = await reddit.subreddit(subreddit_name, fetch=True)
    get = sub.random_rising(limit=1)
    async for i in get:
        embed = discord.Embed(
            title=embed_title,
            url=i.url,
            color=discord.Color.random()
        )
        embed.set_footer(text="See nothing? It's probably a video.")
        embed.set_image(url=i.url)
        await ctx.send(embed=embed)
        

class InternetCommands(commands.Cog, name="Internet"):
    def __init__(self):
        pass

    @commands.command(brief="Get a random fumo")
    async def fumo(self, ctx):
        """Gets a random fumo image from absurdismworld's CDN"""
        with open("./data/extra/fumo_db.txt", "r") as r:
            db = random.choice(str(r.read()).splitlines())
            await ctx.send(db)

    # @commands.command(brief="Get a random neco-arc")
    # async def neco(self, ctx):
    #     """Gets a random neco-arc image (or in some cases, video) from the necoarc subreddit"""
    #     await reddit_random_template(ctx, "necoarc", "Neco-arc")

    @commands.command(brief="AI-generated inspirational quotes.")
    async def inspirobot(self, ctx):
        """Get an AI-generated inspirational quote from the InspiroBot.me website."""
        try:
            link = requests.get("https://inspirobot.me/api?generate=true").content.decode(encoding="utf-8")
            embed = discord.Embed(
                title="InspiroBot",
                color=discord.Color.random()
            )
            embed.set_image(url=link)
            embed.set_footer(text="Generated by InspiroBot.me")
            await ctx.send(embed=embed)
        except ConnectionError:
            print(traceback.format_exc())
            embed = discord.Embed(
                title="InspiroBot",
                description="Failed to get post from InspiroBot api. Is the site down?",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(brief="AI-generated neco-arcs")
    async def tnadne(self, ctx):
        image = f"{aw_tnadne}images/{str(randint(1,488))}.png"
        embed = discord.Embed(
            title="This Neco-Arc Does Not Exist",
            color=discord.Color.gold()
        )

        embed.set_footer(text=f"{aw_tnadne}")
        embed.set_image(url=image)
        await ctx.send(embed=embed)