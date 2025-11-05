import pathlib

from pedalboard import Pedalboard
from pedalboard_native import Reverb, HighShelfFilter, Compressor, PeakFilter
from pedalboard_native.io import AudioFile
from pydub import AudioSegment
from pydub.effects import normalize

from cogs.scripts.bot_global_stuff import speed_change


def generate_club(work_dir: str, fp: str, bpm: str, target_bpm: str):
    sample_bpm = 130
    magic_number = 0.94

    if int(target_bpm) != 0:
        magic_number = float(target_bpm) / float(bpm)

    extension = pathlib.Path(fp).suffix.split(".")[1]

    audio_sample = normalize(AudioSegment.from_file(r"./data/samples/clubgen/climax.wav"), 2)
    sample_mult = (float(bpm) / float(sample_bpm)) * magic_number
    audio_sample = speed_change(audio_sample, sample_mult)

    audio_base = AudioSegment.from_file(fp)
    audio_base = speed_change(audio_base, magic_number)
    audio_base = normalize(audio_base)
    audio_base.export(fp, format=extension)
    audio_base = None
    with AudioFile(fp, "r") as f:
        audio = f.read(f.frames)
        samplerate = f.samplerate
    board = Pedalboard([Reverb(room_size=0.2, wet_level=0.2), HighShelfFilter(140)])
    effected = board(audio, samplerate)
    with AudioFile(f"{work_dir}/chill.wav", 'w', samplerate, effected.shape[0]) as f:
        f.write(effected)
    audio_base = AudioSegment.from_file(f"{work_dir}/chill.wav").overlay(audio_sample, loop=True)
    audio_base.export(f"{work_dir}/chill2.wav", format="wav")
    with AudioFile(f"{work_dir}/chill2.wav", "r") as f:
        audio = f.read(f.frames)
        samplerate = f.samplerate
    board = Pedalboard([Compressor(-10, 2), PeakFilter(100, 10)])
    effected = board(audio, samplerate)
    with AudioFile(f"{work_dir}/chillf.wav", 'w', samplerate, effected.shape[0]) as f:
        f.write(effected)
    compress = AudioSegment.from_file(f"{work_dir}/chillf.wav")
    compress.export(f"{work_dir}/club.mp3", format="mp3")