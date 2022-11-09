import discord
import openai
from discord.ext import commands

from .scripts.service_setup import openai_api_key

openai.api_key = openai_api_key


async def prompt_complete_template(ctx, prompt: str, model: str):
    if len(prompt) > 256:
        embed = discord.Embed(title="OpenAI", description="Your prompt is too long! (>256 characters)")
        await ctx.send(embed=embed)
        return
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    embed = discord.Embed(
        title="OpenAI Prompt + Response",
        description=prompt + " " + response['choices'][0]['text'],
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)


class ArtificialIntelligenceCommands(commands.Cog, name="Artificial Intelligence"):
    def __init__(self):
        pass

    @commands.command(brief="Complete a writing prompt!")
    async def openai_complete(self, ctx, *, prompt: str):
        """
        Uses OpenAI's DaVinci 2 model to follow random instructions, make up a story or do just about
        anything!
        """
        await prompt_complete_template(ctx, prompt, "text-davinci-002")

    @commands.command(name="openai_code", brief="Turn a prompt into code!")
    async def _openai_code(self, ctx, *, prompt: str):
        """
        Uses OpenAI's DaVinci 2 Codex model to turn your prompts into (working) code!\n
        For example, writing 'write a function which prints hello world in python' should work fine.\n
        It is also capable of finishing your code, so you could give it a part of a function and it will finish it.
        """
        await prompt_complete_template(ctx, prompt, "code-davinci-002")
