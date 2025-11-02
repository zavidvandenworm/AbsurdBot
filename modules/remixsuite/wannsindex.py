import glob
import os
from random import choice

here = os.path.dirname(__file__)


def get_random_break() -> str:
    return choice(glob.glob(f'{here}/samples/**/*.wav'))
