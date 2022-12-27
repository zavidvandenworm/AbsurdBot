from pydub import AudioSegment
from pydub.generators import Sine, Sawtooth, Square
from pydub.utils import mediainfo
from pychord import Chord, ChordProgression
from pedalboard import Pedalboard, Reverb, Chorus, Compressor
from pedalboard.io import AudioFile
from random import choice, randint
from librosa import note_to_hz
from bot_global_stuff import speed_change
from pathlib import Path
from glob import glob
from pyrubberband import time_stretch
import numpy

current_dir = Path(__file__).parent
sample_dir = Path(str(current_dir.parents[1])+"\\data\\samples")
drum_samples = glob(str(sample_dir)+"\\drum_loops\\*.wav")

method = "celestrial"

if method == "celestrial":
  celestrial_samples = glob(str(sample_dir) + "\\synth\\celestrial\\*.wav")

bpm = 150
sample_bpm = 150
#bpm is hardcoded for now
segment_length = (60/bpm)*4
print(segment_length)

chords_major = ["CM", "C#M", "DM", "EM", "FM", "F#M", "GM", "AM", "BM"]
chords_minor = ["Cm", "C#m", "Dm", "Em", "Fm", "F#m", "Gm", "Am", "Bm"]

generated = []
for i in range(8):
    generated.append(choice(chords_minor)+str(randint(7, 7)))
print(generated)

def get_sample_array(self):
    return numpy.array(self.array_type, self._data)

chordprogression = ChordProgression(generated)

compile = AudioSegment.silent(0)

generator_volume = -18

for i in chordprogression:
    segment = AudioSegment.silent(int(segment_length*1000))
    if method in ["sine","sawtooth","square"]:
      for note in i.components_with_pitch(3):
          if method == "sine":
            saw = Sine(note_to_hz(note))
          if method == "saw":
            saw = Sawtooth(note_to_hz(note))
          if method == "square":
            saw = Square(note_to_hz(note))
          saw = saw.to_audio_segment(segment_length*1000, generator_volume)
          segment = segment.overlay(saw, 0)
    if method == "celestrial":
      for note in i.components_with_pitch(4):
        thing = AudioSegment.from_file(str(sample_dir)+f"\\synth\\celestrial\\{note}.wav")
        segment = segment.overlay(thing, 0)
    compile += segment
print(compile.duration_seconds)

drum_chosen = choice(drum_samples)
drum_track = AudioSegment.from_file(drum_chosen, format="wav")
#drum_track = speed_change(drum_track, bpm/sample_bpm, int(mediainfo(drum_chosen)['sample_rate']))
drum_track.export("./lord.wav", format="wav")
print(bpm/sample_bpm)
#x = time_stretch(numpy.asarray(drum_track.get_array_of_samples()), int(mediainfo(drum_chosen)['sample_rate']), bpm/sample_bpm)

compile = compile.overlay(drum_track, loop=True)

compile.export("./test.wav", format="wav")

with AudioFile('./test.wav') as f:
  audio = f.read(f.frames)
  samplerate = f.samplerate

board = Pedalboard([Compressor(-5, 1), Reverb(room_size=0.13, wet_level=0.18, dry_level=0.25, width=1, damping=0.75), Chorus(rate_hz=0.1, centre_delay_ms=7, feedback=0.07)])
effected = board(audio, samplerate)

with AudioFile('processed-output.wav', 'w', samplerate, effected.shape[0]) as f:
  f.write(effected)