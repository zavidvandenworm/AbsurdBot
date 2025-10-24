from pedalboard import Pedalboard, Reverb
from pedalboard.io import AudioFile
import sys

from pydub import AudioSegment

from cogs.scripts.paultest import paulstretch_segment

work_dir = sys.argv[1]
local_file = sys.argv[2]

audio_file = AudioSegment.from_file(local_file)
stretch = paulstretch_segment(audio_file)
stretch.export(f"{work_dir}/pad.mp3")