from pedalboard import Pedalboard, Compressor
from pedalboard.io import AudioFile
from pydub.effects import normalize

from bot_global_stuff import *

work_directory = sys.argv[1]
local_file = sys.argv[2]
bpm = float(sys.argv[3])
sound_pack = sys.argv[4]

sound_packs = {}
for i in glob("../data/samples/breakcoregen/*"):
    sound_packs[os.path.basename(i)] = glob(f"{i}/*.wav")


if sound_pack not in sound_packs:
    exit(1)

sample_bpm = 165
sample_multiplier = float(bpm) / float(sample_bpm)

sample_selection = sound_packs[sound_pack]
break_compile = normalize(AudioSegment.from_file(random.choice(sample_selection)), 5)

for i in "123":
    break_compile = break_compile.append(normalize(AudioSegment.from_file(random.choice(sample_selection)), 5),
                                         crossfade=0)

break_compile = speed_change(break_compile, sample_multiplier)

audio_compile = AudioSegment.from_file(local_file)
audio_compile = normalize(audio_compile)
audio_compile = audio_compile.overlay(break_compile, loop=True)
audio_compile.export(f"{work_directory}/overlay-normalize.wav", format="wav")

with AudioFile(f"{work_directory}/overlay-normalize.wav", "r") as f:
    audio = f.read(f.frames)
    samplerate = f.samplerate

board = Pedalboard([Compressor(-7, 6)])
effected = board(audio, samplerate)

with AudioFile(f"{work_directory}/breakcore_generator_unc.mp3", 'w', samplerate, effected.shape[0]) as f:
    f.write(effected)

compress = AudioSegment.from_file(f"{work_directory}/breakcore_generator_unc.mp3")
compress.export(f"{work_directory}/breakcore_generator.mp3", format="mp3")
