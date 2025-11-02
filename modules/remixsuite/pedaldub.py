import numpy as np
from pedalboard import Pedalboard, Reverb
from pedalboard_native import Compressor, Chorus
from pydub import AudioSegment


def audiosegment_to_numpy(audio_segment):
    samples = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
    samples /= 2 ** (8 * audio_segment.sample_width - 1)

    if audio_segment.channels == 2:
        samples = samples.reshape((-1, 2)).T

    return samples, audio_segment.frame_rate


def numpy_to_audiosegment(samples, frame_rate, channels=1):
    if channels == 2:  # Stereo
        samples = samples.T.flatten()
    samples = (samples * (2 ** 15 - 1)).astype(np.int16)
    audio_segment = AudioSegment(
        samples.tobytes(), frame_rate=frame_rate, sample_width=2, channels=channels
    )
    return audio_segment


def reverberate_audiosegment(seg):
    samples, frame_rate = audiosegment_to_numpy(seg)

    board = Pedalboard([
        Reverb(room_size=0.5, wet_level=0.23),
    ])

    channels = 2 if samples.ndim == 2 else 1

    processed_samples = board.process(samples, sample_rate=frame_rate)

    processed_audio = numpy_to_audiosegment(processed_samples, frame_rate, channels)

    return processed_audio


def compress_audiosegment(seg):
    samples, frame_rate = audiosegment_to_numpy(seg)

    board = Pedalboard([Compressor(threshold_db=-2, ratio=2, attack_ms=1.0, release_ms=20)])

    channels = 2 if samples.ndim == 2 else 1
    processed_samples = board.process(samples, sample_rate=frame_rate)
    processed_audio = numpy_to_audiosegment(processed_samples, frame_rate, channels)
    return processed_audio


def process_breakbeat(seg):
    samples, frame_rate = audiosegment_to_numpy(seg)

    board = Pedalboard([Compressor(threshold_db=-2, ratio=2, attack_ms=1.0, release_ms=20),
                        Chorus(rate_hz=0.3, depth=0.25, centre_delay_ms=1.0, feedback=0.1, mix=0.1)])

    channels = 2 if samples.ndim == 2 else 1
    processed_samples = board.process(samples, sample_rate=frame_rate)
    processed_audio = numpy_to_audiosegment(processed_samples, frame_rate, channels)
    return processed_audio
