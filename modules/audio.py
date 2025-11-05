import os
import pathlib
import random
from glob import glob

import ffmpeg
from pedalboard import Pedalboard
from pedalboard_native import Compressor
from pedalboard_native.io import AudioFile
from pydub import AudioSegment
from pydub.effects import normalize

from cogs.scripts.bot_global_stuff import speed_change
from modules.paulstretch import paulstretch_segment
from modules.remixsuite.remix import remix_song

logo = "./data/logo_audio.png"

def generate_audiovisual(fp: str, out_fp: str):
    size_a = [640, 480]

    size = f"{str(size_a[0])}x{str(size_a[1])}"

    output = ffmpeg.input(fp)
    audio = ffmpeg.input(fp)
    output = ffmpeg.filter(output, "showwaves", s=size, mode="cline", rate=25, colors="White|White")
    spectrum = ffmpeg.filter(audio, "showspectrum", size=size, stop=10000, slide="scroll")
    output = ffmpeg.filter([output, spectrum], "blend", all_mode="overlay")

    output = ffmpeg.overwrite_output(ffmpeg.output(output, audio, out_fp, acodec="copy"))
    ffmpeg.run(output)

def convert_to_mp3(fp: str, out_fp: str):
    (
        ffmpeg
        .input(fp)
        .output(out_fp, acodec="libmp3lame", audio_bitrate="192k")
        .run(quiet=True, overwrite_output=True)
    )

def convert_to_mp4(fp: str, out_fp: str):
    (
        ffmpeg
        .input(fp)
        .output(out_fp)
        .run(quiet=True, overwrite_output=True)
    )


def generate_breakcore(work_dir: str, fp: str, out_fp: str, bpm: float):
    sound_packs = []

    for i in glob("./data/samples/breakcoregen/*"):
        sound_packs.append(glob(f"{i}/*.wav"))

    sample_selection = random.choice(sound_packs)

    sample_bpm = 165
    sample_multiplier = float(bpm) / float(sample_bpm)

    break_compile = normalize(AudioSegment.from_file(random.choice(sample_selection)), 5)

    for i in "123":
        break_compile = break_compile.append(normalize(AudioSegment.from_file(random.choice(sample_selection)), 5),
                                             crossfade=0)

    break_compile = speed_change(break_compile, sample_multiplier)

    audio_compile = AudioSegment.from_file(fp)
    audio_compile = normalize(audio_compile)
    audio_compile = audio_compile.overlay(break_compile, loop=True)

    audio_compile.export(f"{work_dir}/overlay-normalize.wav", format="wav")

    with AudioFile(f"{work_dir}/overlay-normalize.wav", "r") as f:
        audio = f.read(f.frames)
        samplerate = f.samplerate

    board = Pedalboard([Compressor(-7, 6)])
    effected = board(audio, samplerate)

    with AudioFile(f"{work_dir}/breakcore_generator_unc.mp3", 'w', samplerate, effected.shape[0]) as f:
        f.write(effected)

    compress = AudioSegment.from_file(f"{work_dir}/breakcore_generator_unc.mp3")
    compress.export(out_fp, format="mp3")

def generate_remixsuite_remix(fp: str, out_fp: str, bpm: float, target_bpm: float | None = None):
    remix = remix_song(fp, bpm, target_bpm)
    remix.export(out_fp, format="mp3")

def generate_logo_video_from_audio(fp: str, out_fp: str):
    img = ffmpeg.input(logo, loop=1, framerate=1)
    aud = ffmpeg.input(fp)

    (
        ffmpeg
        .output(
            img,
            aud,
            out_fp,
            vcodec="libx264",
            acodec="copy",
            shortest=None,
            pix_fmt="yuv420p"
        )
        .overwrite_output()
        .run(quiet=True)
    )

def generate_paulstretch(work_dir: str, fp: str, out_fp: str):
    mp3_fp = os.path.join(work_dir, "tmp.mp3")
    stretched = paulstretch_segment(AudioSegment.from_file(fp))
    stretched.export(mp3_fp, format="mp3", bitrate="320k")
    generate_logo_video_from_audio(mp3_fp, out_fp)

