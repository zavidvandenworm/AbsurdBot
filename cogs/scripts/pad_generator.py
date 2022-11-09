from pedalboard import Pedalboard, Reverb
from pedalboard.io import AudioFile
import sys

work_dir = sys.argv[1]
local_file = sys.argv[2]

with AudioFile(local_file, "r") as f:
    audio = f.read(f.frames)
    samplerate = f.samplerate

board = Pedalboard([Reverb(1, .5, .3, 0)])
effected = board(audio, samplerate)
with AudioFile(f"{work_dir}/pad.mp3", "w", samplerate, effected.shape[0]) as f:
    f.write(effected)
