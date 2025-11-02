import subprocess
import random
from pydub import AudioSegment
from .rythms import rhythms, crazy_rythms


def ffmpeg_chop_with_rhythm(input_path: str, bpm: float, crazy=False, bars=1, out_path="chopped.wav"):
    seg = AudioSegment.from_file(input_path)
    sr = seg.frame_rate

    beat_len = 60.0 / bpm
    rhythm = random.choice(crazy_rythms if crazy else rhythms)

    # Een bar = 4 beats
    total_beats = 4 * bars

    start_beat = random.randint(0, int(len(seg) / 1000 / beat_len) - total_beats)
    start_sec = start_beat * beat_len

    inputs = ["-ss", str(start_sec), "-i", input_path]
    filters = []
    labels = []

    cursor = 0.0
    idx = 0

    for dur_beats, volume, *speed in rhythm:
        dur = dur_beats * beat_len
        s = speed[0] if speed else 1.0

        flt = f"[0:a]atrim=start={cursor}:end={cursor + dur},asetpts=PTS-STARTPTS"
        if s != 1:
            flt += f",atempo={s}"
        if volume != 1:
            gain_db = (volume - 1) * 6
            flt += f",volume={gain_db}dB"

        flt += f"[p{idx}]"
        filters.append(flt)
        labels.append(f"[p{idx}]")

        cursor += dur
        idx += 1

    concat = "".join(labels)
    filters.append(f"{concat}concat=n={len(labels)}:v=0:a=1[out]")

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", ";".join(filters),
        "-map", "[out]", out_path
    ]

    subprocess.run(cmd, check=True)

    return out_path