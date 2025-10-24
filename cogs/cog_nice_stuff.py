import random
import traceback

import discord
import requests
from discord.ext import commands
from random import randint

class NiceCommands(commands.Cog, name="Nice"):
    def __init__(self):
        pass

    @commands.command(brief="Roll a d20")
    async def d20(self, ctx):
        embed = discord.Embed(
            title="d20"
        )

        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/6545/6545894.png")

        roll = randint(1, 20)

        embed.colour = discord.Colour.blue()


        if roll == 20:
            embed.colour = discord.Colour.green()
            message = "🚨🚨🚨🚨YOU ROLLED A TWENNY!!!!! (20) NICE!!🚨🚨🚨🚨"
        elif roll == 1:
            embed.colour = discord.Colour.red()
            message = "you rolled a 1 :(((( that is very low"
        else:
            message = f"You rolled a [{roll}]."

        embed.description = message

        await ctx.send(embed=embed)