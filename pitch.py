import numpy as np

PITCH_NAMES = ("Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si")
#PITCH_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# See https://newt.phys.unsw.edu.au/jw/notes.html
def freq_to_number(f): 
    return 69 + 12*np.log2(f/440.0)

def number_to_freq(n): 
    return 440 * 2.0**((n-69)/12.0)

def pitch_name(n): 
    return PITCH_NAMES[n % 12] + str(int(n/12 - 1))
