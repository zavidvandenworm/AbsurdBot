import asyncio
import io

import os
import pathlib
import tempfile

import discord.ext.commands
from discord.ext import commands

from modules.audio import generate_audiovisual, convert_to_mp3, generate_breakcore, generate_remixsuite_remix, \
    generate_paulstretch
from modules.jobs import TaskManager
from modules.logger import create_logger
from modules.upload import handle_upload
from modules.web_file import WebFile
from .scripts.bot_global_stuff import *
from .scripts.embeds import *

logger = create_logger("audio cog")

class AudioManipulationCommands(commands.Cog, name="Audio"):
    def __init__(self):
        self.task_manager = TaskManager()
        pass

    @commands.command(brief="Audio visualizer")
    async def audiovisual(self, ctx, audio_url):
        await ctx.send("processing, give it a second", ephemeral=True)
        with tempfile.TemporaryDirectory() as tmpdirname:
            dl = WebFile(audio_url)
            if not dl.fetch():
                return await ctx.send("Failed to download file.")
            fp = dl.save(tmpdirname)

            out_path = f"{tmpdirname}/visualizer.mp4"

            job = await self.task_manager.run(generate_audiovisual, fp, out_path)

            if not job.success:
                return await ctx.send("Visualizer failed.")

            await handle_upload(ctx, out_path)

    @commands.command(brief="Convert any audio/video file into a mp3!")
    async def any2mp3(self, ctx, audio_url):
        """
        Takes a direct link to any audio or video file as an argument, and converts it to mp3.
        """
        with tempfile.TemporaryDirectory() as tmpdirname:
            dl = WebFile(audio_url)
            if not dl.fetch():
                return await ctx.send("Failed to download file.")
            fp = dl.save(tmpdirname)

            out_path = f"{tmpdirname}/convert.mp3"

            job = await self.task_manager.run(convert_to_mp3, fp, out_path)

            if not job.success:
                return await ctx.send("Conversion failed.")

            await handle_upload(ctx, out_path)

    @commands.command(brief="Turn any audio file into breakcore!")
    async def breakcore(self, ctx, audio_url, bpm: float):
        """
        Takes a direct link to an audio file, together with BPM and returns a
        breakcorified version of it.
        """
        with tempfile.TemporaryDirectory() as tmpdirname:
            dl = WebFile(audio_url)
            if not dl.fetch():
                return await ctx.send("Failed to download file.")
            fp = dl.save(tmpdirname)

            out_path = f"{tmpdirname}/convert.mp3"

            job = await self.task_manager.run(generate_breakcore, tmpdirname, fp, out_path, bpm)

            if not job.success:
                logger.warn(job.message)
                return await ctx.send("Breakcoregenerator failed.")

            await handle_upload(ctx, out_path)

    @commands.command(brief="Remix a song. Basically breakcoregen v2")
    async def remix(self, ctx, audio_url):
        with tempfile.TemporaryDirectory() as tmpdirname:
            dl = WebFile(audio_url)
            if not dl.fetch():
                return await ctx.send("Failed to download file.")
            fp = dl.save(tmpdirname)

            out_path = f"{tmpdirname}/convert.mp3"

            job = await self.task_manager.run(generate_remixsuite_remix, fp, out_path)

            if not job.success:
                logger.warn(job.message)
                return await ctx.send("Remix failed.")

            await handle_upload(ctx, out_path)

    @commands.command(brief="Turn your audio file into a club banger!")
    async def clubgen(self, ctx, audio_link, bpm, target_bpm: int = 0):
        work_dir = WorkDir()
        audio_local = media_require(audio_link, "audio", work_dir.directory)
        if audio_local is None:
            await ctx.send(embed=e_invalid_generic)
            return
        p = subprocess.Popen(["python3", "./scripts/club_generator.py", work_dir.directory, audio_local,
                              str(bpm), str(target_bpm), url2ext(audio_link)
                              ], shell=False, cwd=os.path.dirname(os.path.realpath(__file__)))
        timer = 0
        while True:
            if p.poll() is not None:
                print(f"completed after {str(timer)} with exit code {str(p.poll())}")
                if p.poll() != 0:
                    await ctx.send(embed=e_breakcoregen_failed)
                    return
                final = f"{work_dir.directory}/club.mp3"
                await ctx.send(file=discord.File(fp=final))
                return
            timer += .5
            await asyncio.sleep(.5)

    @commands.command(brief="Paulstretches audio!")
    async def paulstretch(self, ctx: discord.ext.commands.Context, audio_url):
        await ctx.send("processing, give it a second", ephemeral=True)
        with tempfile.TemporaryDirectory() as tmpdirname:
            dl = WebFile(audio_url)
            if not dl.fetch():
                return await ctx.send("Failed to download file.")
            fp = dl.save(tmpdirname)

            out_path = f"{tmpdirname}/paul.mp4"

            job = await self.task_manager.run(generate_paulstretch, tmpdirname, fp, out_path)

            if not job.success:
                logger.warn(job.message)
                return await ctx.send("Paulstretch failed.")

            await handle_upload(ctx, out_path)

    @commands.command(brief="Append (many) audio files")
    async def audio_append(self, ctx, *args):
        final = AudioSegment.silent(0)
        work_dir = WorkDir()
        for x in args:
            audio_local = media_require(x, "audio", work_dir.directory)
            if audio_local is None:
                await ctx.send(embed=e_invalid_generic)
                return
            final = final.append(AudioSegment.from_file(audio_local), crossfade=0)
        final.export(f"{work_dir.directory}/append.mp3", format="mp3")
        await ctx.send(file=discord.File(fp=f"{work_dir.directory}/append.mp3"))

    @commands.command(brief="Trim an audio/video file (in MS)")
    async def audio_trim(self, ctx, media_url, start_ms: int, end_ms: int = 0):
        work_dir = WorkDir()
        audio_local = media_require(media_url, "audiovideo", work_dir.directory)
        if audio_local is False:
            await ctx.send(embed=e_invalid_generic)
            return
        audio = AudioSegment.from_file(audio_local)
        if end_ms == 0:
            processed = audio[int(start_ms):]
        else:
            processed = audio[int(start_ms):int(end_ms)]
        processed.export(f"{work_dir.directory}/cut.mp3", format="mp3")
        await ctx.send(file=discord.File(fp=f"{work_dir.directory}/cut.mp3"))

    # @commands.command(brief="Compress an audio file using Xfer's OTT")
    # async def plugin(self, ctx, audio_file):
    #     work_dir = WorkDir()
    #     audio_local = media_require(audio_file, "audio", work_dir.directory)
    #     if audio_local is False:
    #         await ctx.send(embed=e_invalid_generic)
    #         return
    #     p = subprocess.Popen(["python3", "./vst-process.py", work_dir.directory, audio_local], shell=False,
    #                          cwd=os.path.dirname(os.path.realpath(__file__)))
    #     timer = 0
    #     while True:
    #         if p.poll() is not None:
    #             print(f"completed after {str(timer)} with exit code {str(p.poll())}")
    #             if p.poll() != 0:
    #                 print("failed to execute ott!")
    #                 await ctx.send(embed=e_ott_failed)
    #                 return
    #             final = f"{work_dir.directory}/ott.mp3"
    #             await ctx.send(file=discord.File(fp=final))
    #             return
    #         timer += .5
    #         await asyncio.sleep(.5)

    @commands.command(brief="A drum machine!")
    async def drum_machine(self, ctx, beats: str, bpm: int, sample: str, overlay_audio: str = None):
        global drummachine_library
        work_dir = WorkDir()
        overlay_local = None
        beat_out = f"{work_dir.directory}/{str(ctx.author.id)}.wav"
        if sample not in drummachine_library:
            await ctx.send(embed=e_drummachine_snf)
            return False
        if not all(c in '01' for c in beats):
            await ctx.send(embed=e_drummachine_bb)
            return False
        if overlay_audio is not None:
            overlay_local = media_require(overlay_audio, "audio")
            if overlay_local is None:
                await ctx.send(embed=e_drummachine_bo)
                return False
        sample = AudioSegment.from_file(drummachine_library[sample])
        beat_length = (60 / (bpm * 4)) * 1000
        silent_track = AudioSegment.silent(duration=len(beats) * beat_length)
        overlay = silent_track.overlay(AudioSegment.silent(duration=1))
        current_beat = 0
        for i in beats:
            if i == "1":
                overlay = overlay.overlay(sample, position=(beat_length * float(current_beat)))
                # print(f"beat at {str(beat_length * float(current_beat))} ms CURRENT BEAT {str(current_beat)}")
            current_beat += 1
        if overlay_audio is not None:
            add_in = AudioSegment.from_file(overlay_local)
            overlay = add_in.overlay(overlay, position=0)
            os.remove(overlay_local)
        overlay.export(beat_out)
        await ctx.send(file=discord.File(fp=beat_out))
        os.remove(beat_out)

    @commands.command(brief="Experimental break generator")
    async def breakgen(self, ctx, bpm: int = 165):
        output = io.BytesIO()
        kicks, snares, garbles, overlays = \
            [glob("./data/samples/breakgen/kick/*")], \
            [glob("./data/samples/breakgen/snare/*")], \
            [glob("./data/samples/breakgen/garble/*")], \
            [glob("./data/samples/breakgen/overlay/*")]

        patterns = [
            "1321323313213233",
            "11233123112331231123313231231232",
            "13312132121323331331213212132323"
        ]
        kick, snare, garble, overlay, pattern = \
            AudioSegment.from_file(random.choice(kicks[0])), \
            AudioSegment.from_file(random.choice(snares[0])), \
            AudioSegment.from_file(random.choice(garbles[0])), \
            AudioSegment.from_file(random.choice(overlays[0])), \
            random.choice(patterns)
        lookup_table = {
            "1": kick,
            "2": snare,
            "3": garble
        }
        final = AudioSegment.silent(0, 44100)

        for beat in pattern:
            final = final.append(lookup_table[beat], 0)
        final = final.overlay(overlay, 0, 1)
        final.export(output, format="mp3")
        output.seek(0)
        await ctx.send(file=discord.File(fp=output, filename="break.mp3"))
