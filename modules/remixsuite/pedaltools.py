import logging
import random
import sys
from io import BytesIO
from os import access, R_OK

from pydub import AudioSegment
from pydub.effects import normalize

default_audio_format = "wav"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))


def stretch_segment(seg: AudioSegment, amount: float) -> AudioSegment:
    new_frame_rate = int(seg.frame_rate * amount)
    seg = seg._spawn(seg.raw_data, overrides={"frame_rate": new_frame_rate})

    return seg


def detect_leading_silence(seg: AudioSegment, silence_threshold=-50.0, chunk_size=10):
    trim_ms = 0  # ms

    assert chunk_size > 0  # to avoid infinite loop
    while seg[trim_ms:trim_ms + chunk_size].dBFS < silence_threshold and trim_ms < len(seg):
        trim_ms += chunk_size

    return trim_ms


def remove_leading_silence(seg: AudioSegment):
    start_trim = detect_leading_silence(seg)
    end_trim = detect_leading_silence(seg.reverse())

    duration = len(seg)
    trimmed_sound = seg[start_trim:duration - end_trim]

    logger.info(
        "leading silence trim: trimmed " + str(start_trim) + " ms off the start and " + str(
            end_trim) + " ms off the end.")

    return trimmed_sound


def prepare_audio(file: str | BytesIO | AudioSegment, audio_format: str | None = None,
                  skip_trim: bool = False) -> AudioSegment | None:
    if isinstance(file, str):
        if not access(file, R_OK):
            logger.error("the path (as string) provided to prepare_audio cannot be read. Returning None")
            return None
        audio_format = audio_format or file.split(".")[-1]
    else:
        audio_format = audio_format or default_audio_format

    logger.info(
        "the audio format in prepare_audio has been set to " + audio_format + ". please ensure this is expected.")

    try:
        with open(file, 'rb') if isinstance(file, str) else file as stream:
            seg = AudioSegment.from_file(stream, format=audio_format)

        seg = normalize(seg)

        if not skip_trim:
            seg = remove_leading_silence(seg)

        logger.info("prepare_audio has processed the audio file successfully.")
        return seg
    except Exception as e:
        logger.error(
            "An exception occurred in prepare_audio, either while reading the file, normalizing the audio or trimming"
            " the file. See exception below. Returning None.\n" + str(e))
        return None


def append_segments(segments: list[AudioSegment]) -> AudioSegment:
    appended = AudioSegment.empty()

    for idx, i in enumerate(segments):
        appended = appended.append(i, crossfade=5 if idx > 0 else 0)
        logger.info(f"appending segment with length {len(i)} ms.")

    return appended


def ensure_chunk_conforms_bpm(seg: AudioSegment, bpm: float) -> AudioSegment:
    duration = get_segment_duration(bpm)
    chunk_seg = AudioSegment.silent(duration=duration)

    logger.info(
        f"matching audio segment with duration of {len(seg)} MS to match {bpm} BPM. New length is {duration * 1000} MS")

    seg = seg[:duration * 1000]
    seg = chunk_seg.overlay(seg)

    return seg


def get_segment_duration(bpm: float) -> float:
    return 240 / bpm


def random_block_position_within_range(block_range: int, block_length: int) -> (int, int):
    if block_length > block_range:
        raise ValueError(
            f"tried fitting block with length {block_length} in range {block_range}. that does not fit.")

    max_start = block_range - block_length

    beats_per_chunk = block_range // block_length
    start_position = (random.randint(0, beats_per_chunk) * block_length) % block_range
    
    end_position = start_position + block_length

    return start_position, end_position
