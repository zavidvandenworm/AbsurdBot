import traceback

import discord
from discord import Interaction, Component
from discord.ext import commands
import time
from datetime import datetime

from modules.logger import create_logger

logger = create_logger('general')


class GenericCog(commands.Cog, name="General"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener(name='on_command')
    async def print(self, ctx):
        server = ctx.guild.name
        user = ctx.author
        command = ctx.message.content

        logger.info(f'[{user}@{server}] {command}')

    @commands.Cog.listener(name='on_command_error')
    async def error_handle(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass

        server = ctx.guild.name
        user = ctx.author
        command = ctx.command

        logger.warn(f'{server} > {user} > {command} > {error}')

        if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument, commands.TooManyArguments)):
            await ctx.send(embed = discord.Embed(
                title = 'Missing, invalid or too many argument(s).',
                description=error
            ))
            return

        embed = discord.Embed(
            title="Something is broken",
            description="An error has occured while running that command.",
            color=discord.Color.red()
        )

        await ctx.send(embed=embed)

    @commands.Cog.listener(name='on_message')
    @commands.guild_only()
    async def i_dislike_arcane(self, ctx):
        if ctx.guild.id != 924333267845541989:
            return
        if ctx.author.id != 437808476106784770:
            return
        await ctx.add_reaction("🤓")

    @commands.command(brief="Sends a bot invite via DM")
    async def invite(self, ctx):
        view = discord.ui.View()

        view.add_item(discord.ui.Button(
            label="Click here to invite",
            style=discord.ButtonStyle.primary,
            url=f"https://discord.com/oauth2/authorize?client_id={self.bot.application_id}&scope=bot&permissions=446676913216)"))

        await ctx.send(view=view)