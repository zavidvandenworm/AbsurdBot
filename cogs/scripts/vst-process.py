from pedalboard import Pedalboard, load_plugin
from pedalboard.io import AudioFile
import sys
from pydub import AudioSegment

work_dir = sys.argv[1]
audio_local = sys.argv[2]
vst_location = sys.argv[3]

vst = load_plugin(vst_location)

with AudioFile(audio_local, 'r') as f:
  audio = f.read(f.frames)
  samplerate = f.samplerate
effected = vst(audio, samplerate)

board = Pedalboard([vst])

effected = board(audio, samplerate)

with AudioFile(f'{work_dir}/processed-output.wav', 'w', samplerate, effected.shape[0]) as f:
  f.write(effected)

compress = AudioSegment.from_file(f"{work_dir}/processed-output.wav")
compress.export(f"{work_dir}/vst.mp3", format="mp3")
