import numpy as np
import sys

from pydub import AudioSegment



work_dir = sys.argv[1]
local_file = sys.argv[2]

def pydub_to_np(audio: AudioSegment) -> tuple[np.ndarray, int]:
    """
    Converts pydub audio segment into np.float32 of shape [duration_in_seconds*sample_rate, channels],
    where each value is in range [-1.0, 1.0].
    Returns tuple (audio_np_array, sample_rate).
    """
    return np.array(audio.get_array_of_samples(), dtype=np.float32).reshape((-1, audio.channels)) / (
            1 << (8 * audio.sample_width - 1)), audio.frame_rate

def stretch(y: np.ndarray, stretch_factor: float, window_size: int = 8192) -> np.ndarray:
    # prepare input buffer

    x = y.copy()

    if len(x.shape) == 1:
        x = np.expand_dims(x, axis=1)

    transpose = False
    if x.shape[0] < x.shape[1]:
        transpose = True
        x = x.T

    # prepare output buffer

    n_channels = x.shape[1]
    output_length = int(np.ceil(x.shape[0] * stretch_factor))
    n_frames = int(output_length // (0.5 * window_size))
    full_output_length = (n_frames + 1) * int(0.5 * window_size)
    output_buffer = np.zeros_like(x, shape=(full_output_length, n_channels))

    # calculate window

    window = np.sin(np.linspace(0, np.pi, window_size))
    window = np.expand_dims(window, axis=1)
    window = np.tile(window, (1, n_channels))

    # process frames

    for n in range(int(n_frames)):
        output_i = int(n * window_size * 0.5)
        input_i = int(np.round(output_i / stretch_factor))

        frame = x[input_i:input_i + window_size].copy()

        # extend incomplete last frame to fill entire window
        if frame.shape[0] < window_size:
            frame = x[input_i:].copy()
            pad_amount = window_size - frame.shape[0]
            frame = np.pad(frame, ((0, pad_amount), (0, 0)))

        frame *= window

        fft = np.fft.rfft(frame, axis=0)

        random_phases = np.random.uniform(-np.pi, np.pi, size=fft.shape[0])
        random_phases = np.expand_dims(random_phases, axis=1)
        random_phases = np.tile(random_phases, (1, n_channels))

        fft *= np.exp(1.j * random_phases)

        frame = np.fft.irfft(fft, axis=0)

        frame *= window

        output_buffer[output_i:output_i + window_size] += frame

    if transpose:
        output_buffer = output_buffer.T

    return output_buffer

def paulstretch_segment(audio_file: AudioSegment) -> AudioSegment:
    audio_np = pydub_to_np(audio_file)

    stretched = stretch(audio_np[0], 16)

    stretched_audio = AudioSegment(
        (stretched * (1 << (8 * audio_file.sample_width - 1))).astype(
            np.int16 if audio_file.sample_width == 2 else np.int32).tobytes(),
        frame_rate=audio_file.frame_rate,
        sample_width=audio_file.sample_width,
        channels=audio_file.channels
    )

    return stretched_audio



audio_filey = AudioSegment.from_file(local_file)
stretchy = paulstretch_segment(audio_filey)
stretchy.export(f"{work_dir}/pad.mp3")