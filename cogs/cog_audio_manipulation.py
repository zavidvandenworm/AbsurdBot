import io

import os
import tempfile

import discord.ext.commands
from discord.ext import commands

from modules.audio import generate_audiovisual, generate_breakcore, generate_remixsuite_remix, \
    generate_paulstretch
from modules.classic_music_generators.chordgen import generate_chord
from modules.classic_music_generators.club import generate_club
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
        self.task_manager.JOB_TIME_LIMIT = 200
        pass

    @commands.command(brief="Audio visualizer")
    async def audiovisual(self, ctx, audio_url):
        await ctx.send("processing, give it a second", ephemeral=True)
        with tempfile.TemporaryDirectory() as tmpdirname:
            dl = WebFile(audio_url)
            if not dl.check():
                return await ctx.send("Failed to download file.")
            fp = dl.save(tmpdirname)

            out_path = f"{tmpdirname}/visualizer.mp4"

            job = await self.task_manager.run(generate_audiovisual, fp, out_path)

            if not job.success:
                return await ctx.send("Visualizer failed.")

            await handle_upload(ctx, out_path)

    @commands.command(brief="Turn any audio file into breakcore!")
    async def breakcore(self, ctx, audio_url, bpm: float):
        """
        Takes a direct link to an audio file, together with BPM and returns a
        breakcorified version of it.
        """
        with tempfile.TemporaryDirectory() as tmpdirname:
            dl = WebFile(audio_url)
            if not dl.check():
                return await ctx.send("Failed to download file.")
            fp = dl.save(tmpdirname)

            out_path = f"{tmpdirname}/convert.mp3"

            job = await self.task_manager.run(generate_breakcore, tmpdirname, fp, out_path, bpm)

            if not job.success:
                logger.warn(job.message)
                return await ctx.send("Breakcoregenerator failed.")

            await handle_upload(ctx, out_path)

    @commands.command(brief="Remix a song. Basically breakcoregen v2")
    async def remix(self, ctx, audio_url: str, bpm: float, target_bpm: float | None = None):
        with tempfile.TemporaryDirectory() as tmpdirname:
            dl = WebFile(audio_url)
            if not dl.check():
                return await ctx.send("Failed to download file.")
            fp = dl.save(tmpdirname)

            out_path = f"{tmpdirname}/convert.mp3"

            job = await self.task_manager.run(generate_remixsuite_remix, fp, out_path, bpm, target_bpm)

            if not job.success:
                logger.warn(job.message)
                return await ctx.send("Remix failed.")

            await handle_upload(ctx, out_path)

    @commands.command(brief="Turn your audio file into a club banger!")
    async def club(self, ctx, audio_url, bpm, target_bpm: int = 0):
        with tempfile.TemporaryDirectory() as tmpdirname:
            dl = WebFile(audio_url)
            if not dl.check():
                return await ctx.send("Failed to download file.")
            fp = dl.save(tmpdirname)

            out_path = f"{tmpdirname}/club.mp3"

            job = await self.task_manager.run(generate_club, tmpdirname, fp, bpm, target_bpm)

            if not job.success:
                await ctx.send("Club generator failed.")

            await handle_upload(ctx, out_path)


    @commands.command(brief="Generate a chord progression.")
    async def chord(self, ctx: commands.Context, bpm: float = 160):
        with tempfile.TemporaryDirectory() as tmpdirname:
            out_fp = f"{tmpdirname}/chord.mp3"
            job = await self.task_manager.run(generate_chord, out_fp, bpm)
            if not job.success:
                return await ctx.send(f"Chord generator failed. {job.message}")
            await handle_upload(ctx, out_fp)


    @commands.command(brief="Paulstretches audio.")
    async def paulstretch(self, ctx: discord.ext.commands.Context, audio_url):
        await ctx.send("processing, give it a second", ephemeral=True)
        with tempfile.TemporaryDirectory() as tmpdirname:
            dl = WebFile(audio_url)
            if not dl.check():
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
