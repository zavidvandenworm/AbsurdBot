import traceback

import discord
from discord.ext import commands
import time
from datetime import datetime


class GenericCog(commands.Cog, name="Internal"):
    def __init__(self):
        pass

    @commands.Cog.listener(name='on_command')
    async def print(self, ctx):
        server = ctx.guild.name
        user = ctx.author
        command = ctx.message.content
        print(f'{str(datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))} - {server} > {user} > {command}')

    @commands.Cog.listener(name='on_command_error')
    async def error_handle(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        server = ctx.guild.name
        user = ctx.author
        command = ctx.command
        print(traceback.print_exc())
        print(f'{server} > {user} > {command} > {error}')
        embed = discord.Embed(
            title="Command error",
            description=error,
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener(name='on_message')
    @commands.guild_only()
    async def okarcanethanks(self, ctx):
        if ctx.guild.id != 924333267845541989:
            return
        if ctx.author.id != 437808476106784770:
            return
        await ctx.reply("ok arcane thanks")

    @commands.command(brief="Sends a bot invite via DM")
    async def invite(self, ctx):
        embed = discord.Embed(
            title="Absurdibot invite",
            description="[Click here](https://discord.com/oauth2/authorize?client_id=948227722382036992&scope=bot&permi"
                        "ssions=446676913216)"
        )
        await ctx.send(embed=embed)
