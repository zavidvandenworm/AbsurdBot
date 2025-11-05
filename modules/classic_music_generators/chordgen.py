from pydub import AudioSegment
from pychord import ChordProgression
from pydub.generators import Sine, Sawtooth, Square, Triangle
from pydub.effects import low_pass_filter
from pydub.utils import make_chunks
from random import choice

def midi_to_freq(midi_note: int) -> float:
    return 440.0 * (2 ** ((midi_note - 69) / 12))

NOTE_OFFSETS = {
    "C":0, "C#":1, "Db":1,
    "D":2, "D#":3, "Eb":3,
    "E":4,
    "F":5, "F#":6, "Gb":6,
    "G":7, "G#":8, "Ab":8,
    "A":9, "A#":10, "Bb":10,
    "B":11
}

def note_to_hz(note: str) -> float:
    base = note[:-1]
    octave = int(note[-1])
    midi = 12 * (octave + 1) + NOTE_OFFSETS[base]
    return midi_to_freq(midi)

GORESHIT_JITTER_PATTERN = [*[1,0]*12, *[1, 1]*4] # dabadabadabadabadabadaba baaaaaaaaaaaa

DRAMATIC_CHORDS = [
    ["Am", "Fm", "Cm", "Dm"],
    ["Bm", "A", "Em", "F#m"]
]

def jitter(segment: AudioSegment) -> AudioSegment:
    split_len = len(segment) / 32

    split_silent = AudioSegment.silent(duration=split_len)

    split = make_chunks(segment, split_len)

    gore_combined = AudioSegment.silent(duration=0)

    for i, y in enumerate(GORESHIT_JITTER_PATTERN):
        if GORESHIT_JITTER_PATTERN[i] == 1:
            gore_combined += split[i]
        else:
            gore_combined += split_silent

    return gore_combined

def generate_single_chord(notes: list[str], sound: str, duration: float, volume: float) -> AudioSegment:
    combined = AudioSegment.silent(duration=duration)

    for note in notes:
        freq = note_to_hz(note)
        match sound:
            case "saw":
                generator = Sawtooth(freq=freq)
            case "sine":
                generator = Sine(freq=freq)
            case "triangle":
                generator = Triangle(freq=freq)
            case _:
                generator = Square(freq=freq)

        generate = generator.to_audio_segment(duration=duration, volume=volume)
        combined = combined.overlay(generate, loop=False)

    return jitter(combined)

def generate_chord(out_fp: str, bpm: int = 170):
    method = choice(["sine", "saw", "square"])

    chord_progression = ChordProgression(choice(DRAMATIC_CHORDS))

    compiled = AudioSegment.silent(0)

    length = (60 / bpm) * 4000

    for i in chord_progression:
        notes = [*i.components_with_pitch(2), *i.components_with_pitch(5)]

        segment = generate_single_chord(notes, method, length, -18)

        compiled += segment

    compiled += compiled

    compiled = low_pass_filter(compiled, 3000)

    # stretched = paulstretch_segment(compiled, 8)

    compiled.export(out_fp, format="mp3")
