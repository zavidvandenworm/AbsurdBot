import discord
from .bot_global_stuff import drummachine_library
from glob import glob
from os.path import basename
e_superuser = discord.Embed(
    title="You are not a superuser!",
    description="You are not added to the superuser group.",
    color=discord.Color.red()
)
e_banned = discord.Embed(
    title="You are blacklisted from the bot.",
    description="You can not use commands while you're blacklisted.",
    color=discord.Color.red()
)

e_invalid_av = discord.Embed(
    title="Invalid URL",
    description="Could not get audio from the given URL. Is it a direct link (ends in .mp4, .wav etc)?",
    color=discord.Color.red()
)

e_breakcoregen_failed = discord.Embed(
    title="Breakcore Generator",
    description="Failed to process file!",
    color=discord.Color.red()
)

i_webhost = discord.Embed(
    title="Free static website hosting",
    description="Host your own static (html/js/css etc, no server side scripting) website for 0$!!!"
                "\nUse the following subcommands to manage your domain."
)
i_webhost.add_field(
    name="General command syntax",
    value=f"The following commands generally follow the same syntax: command subcommand source variable.\n"
          f"For example: to upload a file with a target filename of 'index.html' in the root dir, you would type ```"
          f"$web upload https://www.example.com/anything.html ./index.html```"
)

e_youtube_toobig = discord.Embed(
    title="Too big!",
    description="The audio file is too big to be sent over discord!"
)

e_notagif = discord.Embed (
    title="Supplied URL doesn't seem to be a GIF!",
    color=discord.Color.red()
)

e_notavideo = discord.Embed (
    title="Supplied URL doesn't seem to be a video!",
    color=discord.Color.red()
)

e_notaudio = discord.Embed (
    title="Supplied URL doesn't seem to be an audio file!",
    color=discord.Color.red()
)

e_toolarge = discord.Embed(
    title="FIle is too large!",
    description="The supplied file (or command output) is too large to handle/send!",
    color=discord.Color.red()
)

e_invalid_generic = discord.Embed(
    title="Generic error",
    description="An error occured while processing that command, are all inputs valid?",
    color=discord.Color.red()
)

e_ott_failed = discord.Embed(
    title="OTT failed.",
    description="An error occured while processing. sorry :/",
    color=discord.Color.red()
)

i_vc = discord.Embed(
    title="Voice Chat Commands",
    description="A bunch of commands for voice chat stuff like playing audio files."
)

ls_breakcoregen = discord.Embed(
    title="Breakcoregen Sample Packs",
    description="Name + amount of unique samples"
)
for i in glob(r"./cogs/samples/breakcoregen/*"):
    ls_breakcoregen.add_field(
        name=basename(i),
        value=str(len(glob(f"{i}/*.wav")))
    )

ls_drummachine = discord.Embed(
    title="Drum machine samples",
    description=""
)
for i in drummachine_library:
    ls_drummachine.add_field(
        name=basename(i),
        value="."
)

e_daw_audio = discord.Embed(
    title="AbsurdDAW",
    description="Invalid audio file supplied!",
    color=discord.Color.red()
)

e_drummachine_snf = discord.Embed(
                title="Sample not found!",
                description="That sample is not in the sample list. Run $list_samples drum_machine to get a list of all"
                            "available samples!",
                color=discord.Color.red()
            )

e_drummachine_bb = discord.Embed(
                title="Bad beat string!",
                description="A beat string can only contain 0 and 1. \nExample: 1000100010001000",
                color=discord.Color.red()
            )

e_drummachine_bo = discord.Embed(
                    title="Could not load overlay audio!",
                    description="Failed to download the supplied link. Are you sure it's a direct link to an "
                                "audio file?",
                    color=discord.Color.red()
                )

e_data_badimage = discord.Embed(
            title="Image error",
            description="The supplied url does not seem to be an image. "
                        "Was it a direct url? (ends in .png, .jpeg etc.)",
            color=discord.Color.red()
        )
