import pygame, sys
import pygame.freetype
from pygame.locals import *

import numpy as np
from scipy import io, signal
from piano import draw_piano
from pitch import freq_to_number, pitch_name

import matplotlib.pyplot as plt

AUDIO_FILE = "audio/piano_c_major_scale.wav"
#AUDIO_FILE = "audio/alina_dry.wav"

SCREEN_WIDTH        = 1248 # 24 * 52 (count of white keys)
SCREEN_HEIGHT       = 450
FPS                 = 30

FFT_WINDOW_SECONDS  = 0.25 # how many seconds of audio make up an FFT window
PLAY_ORIGINAL       = True
TOP_NOTES_COUNT     = 2
FREQ_LOWEST         = 27
FREQ_HIGHEST        = 4200

def load_audio_data(audio_file):
    # Read data from file
    sample_rate, data = io.wavfile.read(audio_file)
    print(f"Sample rate: {sample_rate}, type: {data.dtype}, duration: {len(data)/sample_rate}")

    # Normalize data to range -1.0 .. +1.0
    # See: https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.read.html
    if data.dtype == "int32":
        data = data.astype(np.float64) / (2**31)
        data = data.astype(np.float32)
    elif data.dtype == "int16":
        data = data.astype(np.float32) / (2**15)
    elif data.dtype == "uint8":
        data = (data.astype(np.float32) - 127.5) / 127.5
    else:
        data = data.astype(np.float32)

    return sample_rate, data

def play_tone(freq, time, volume = 0.5):
    count = int(44100*time)
    ramp = int(count*0.2)

    buff = np.sin(2 * np.pi * np.arange(count) * freq / 44100)

    ramp_effect = np.concatenate((np.linspace(0, 1, ramp, False),
                                  np.full((count - 2*ramp,), 1, dtype=float),
                                  np.linspace(1, 0, ramp, False)))
    buff = buff * ramp_effect * volume

    #plt.plot(buff)
    #plt.show()

    sound = pygame.mixer.Sound(buff.astype(np.float32))
    sound.play(0)

if __name__ == "__main__":
    sample_rate, audio_data = load_audio_data(AUDIO_FILE)

    pygame.mixer.init(frequency=sample_rate, size=32, channels=2)
    pygame.init()
    pygame.display.set_caption('Alina PyPiano')
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock  = pygame.time.Clock()
    font   = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 30)

    # Play original sound
    if PLAY_ORIGINAL:
        sound = pygame.mixer.Sound(audio_data)
        sound.play(0)

    # Get the first channel of multi-channel audio
    audio_channel = np.array(audio_data.T[0])

    SAMPLES_IN_WINDOW = int(sample_rate * FFT_WINDOW_SECONDS)
    AUDIO_DURATION    = int(len(audio_channel) / sample_rate)
    FRAME_SAMPLES     = int(sample_rate / FPS) # audio samples per video frame

    # Hanning window function
    window_effect = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, SAMPLES_IN_WINDOW, False)))
    #plt.plot(window_effect)
    #plt.show()

    for current_frame in range(AUDIO_DURATION*FPS):
        ###########################
        # Data processing
        ###########################

        # Cut the window
        window_start = FRAME_SAMPLES * current_frame
        window = audio_channel[window_start : window_start + SAMPLES_IN_WINDOW]

        # Apply FFT, get power spectral density
        fhat = np.fft.rfft(window * window_effect)
        PSD = (fhat * np.conj(fhat) / SAMPLES_IN_WINDOW).real

        freq = (sample_rate / SAMPLES_IN_WINDOW) * np.arange(SAMPLES_IN_WINDOW)

        # Pick frequencies of real piano
        PSD  = PSD[FREQ_LOWEST:FREQ_HIGHEST]
        freq = freq[FREQ_LOWEST:FREQ_HIGHEST]

        # Find power peaks in FFT output
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html
        peak_indexes, _ = signal.find_peaks(PSD, height=0.5, distance=10)

        ###########################
        # Drawing in PyGame
        ###########################

        # Draw PSD chart
        PSD_draw = 250-PSD*10
        freq_draw = freq * (SCREEN_WIDTH / len(freq))

        chart_data = np.vstack((freq_draw, PSD_draw)).T
        pygame.draw.aalines(screen, "lime", False, chart_data)

        # Highlight all peaks
        for x in peak_indexes:
            pygame.draw.circle(screen, "blue", (freq_draw[x], PSD_draw[x]), 3, 2)
 
        # Pick N first peaks
        active_notes = []
        for x in peak_indexes[0:TOP_NOTES_COUNT]:
            f = freq[x]
            key_number = int(round(freq_to_number(f)))
            name = pitch_name(key_number)
            active_notes.append(key_number - 21)

            # Draw pitch name
            label, _ = font.render(name, "white", size=16)
            screen.blit(label, (freq_draw[x], 260))

            # Console feedback
            print(f"Frequency: {f} Hz, Number: {key_number}, Pitch: {name}")

            # Audio feedback
            if not PLAY_ORIGINAL:
                tone_volume = np.clip(PSD[x]/20, 0, 0.7)
                play_tone(f, 1/10, tone_volume)

        # Draw piano
        piano = draw_piano((SCREEN_WIDTH, 150), active_notes)
        screen.blit(piano, (0, SCREEN_HEIGHT-150))

        ###########################
        # PyGame loop maintenance
        ###########################

        # Diisplay current frame
        pygame.display.flip()

        # Process PyGame events
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit(0)

        # Limit FPS
        clock.tick(FPS)
        # Clear screen for the next frame
        screen.fill((0,0,0))

# TODO:
# - Realtime input from microphone
# - Adjust frequency chart to align with piano on X axis
# - Make piano key highlight color depend on PSD
# - Click piano key -> generate tone
# - Check if FREQ_LOWEST/FREQ_HIGHEST is applied correctly
#
