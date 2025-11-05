import logging
import pathlib
import random
import sys
import tempfile
from io import BytesIO
from random import shuffle

from pydub import AudioSegment
from pydub.effects import normalize
from pydub.utils import make_chunks
from typing_extensions import BinaryIO

from .chop_with_rhythm import ffmpeg_chop_with_rhythm
from .pedaldub import compress_audiosegment, process_breakbeat
from .pedaltools import prepare_audio, stretch_segment, random_block_position_within_range, \
    append_segments, get_segment_duration
from .rythms import crazy_rythms, rhythms
from .wannsindex import get_random_break

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

SAMPLE_PACK_BPM = 165.0
MAKEUP_GAIN = 2.0
DEFAULT_AUDIO_FORMAT = "wav"


def get_random_sections_from_segment(seg: AudioSegment, bpm: float) -> AudioSegment:
    dice_duration = get_segment_duration(bpm) * 1000
    print(f"---------- {dice_duration} ----------")

    s = make_chunks(seg, dice_duration)

    loudness_sort = sorted(s, key=lambda c: c.dBFS, reverse=True)

    pick = loudness_sort[:12]
    shuffle(pick)
    pick = pick[:4]

    diced_segments = []

    for i, p in enumerate(pick):
        diced_seg = apply_random_rhythm_to_segment(p, bpm, i % 4 == 0)
        diced_segments.append(diced_seg)

    appended_segments = append_segments(diced_segments)

    return appended_segments


def apply_rhythm_to_segment(seg: AudioSegment, bpm: float, rhythm: list[(int, int, int)]) -> AudioSegment:
    segment_duration = get_segment_duration(bpm) * 1000

    dice = []

    for beat in rhythm:
        take = beat[0] * segment_duration

        seg_take = stretch_segment(seg, beat[2])[:take] if len(beat) > 2 else seg[:take]
        seg_take += -50 + (beat[1] * 50)
        dice.append(seg_take)

    return append_segments(dice)


def apply_random_rhythm_to_segment(seg: AudioSegment, bpm: float, crazy: bool) -> AudioSegment:
    selected = rhythms[random.randint(0, len(rhythms) - 1)] if not crazy else crazy_rythms[
        random.randint(0, len(crazy_rythms) - 1)]
    return apply_rhythm_to_segment(seg, bpm, selected)


def get_chopped_segment_bar(seg: AudioSegment, bpm: float) -> AudioSegment:
    chops = []

    for i in range(4):
        chops.append(
            apply_random_rhythm_to_segment(normalize(get_random_sections_from_segment(seg, bpm)), bpm, i % 2 == 0))

    return append_segments(chops)


def overlay_instruments(seg: AudioSegment, bpm: float, breaks: bool):
    if breaks:
        break_sample = prepare_audio(get_random_break(), skip_trim=True)
        break_sample = stretch_segment(break_sample, bpm / 165)
        break_sample = process_breakbeat(break_sample)
        seg = seg.overlay(break_sample, loop=True)

    return seg


def overlay_break(seg: AudioSegment, bpm: float):
    break_sample = prepare_audio(get_random_break(), skip_trim=True) - 2
    break_sample = stretch_segment(break_sample, bpm / 165)
    break_sample = process_breakbeat(break_sample)
    seg = seg.overlay(break_sample, loop=True)

    return seg

def remix_song_original(sample: str, audio_format: str | None = None) -> AudioSegment:
    bpm = 150.0

    sample = prepare_audio(sample, audio_format)

    tf = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sample.export(tf.name, format="wav")

    temp = ffmpeg_chop_with_rhythm(tf.name, bpm)

    chopped = AudioSegment.from_file(temp)

    chopped += 2

    first_break_section = overlay_instruments(chopped, bpm, True)
    second_break_section = overlay_instruments(chopped, bpm, True)

    track = append_segments([
        append_segments([chopped, chopped]).fade_in(len(chopped)),

        first_break_section,
        second_break_section,
        chopped[len(chopped) * 0.5:],
        first_break_section[:len(first_break_section) * 0.5],
        second_break_section,
        chopped.fade_out(len(chopped)),
    ])

    track = track + 3

    track = compress_audiosegment(track)

    return track


def remix_song(sample: str, bpm: float, target_bpm: float | None = None) -> AudioSegment:
    sample = prepare_audio(sample, pathlib.Path(sample).suffix.split(".")[1])

    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_fp = f"{tmpdirname}/temp.wav"

        chops = get_random_sections_from_segment(sample, bpm)

    track = AudioSegment.silent(0)

    for c in chops:
        track += c

    track = compress_audiosegment(track)

    if target_bpm is not None:
        stretch_rate = target_bpm / bpm
        track = stretch_segment(track, stretch_rate)

    return track
