import pygame, sys
import pygame.freetype
from pygame.locals import *

import numpy as np
from scipy import io, signal
from piano import draw_piano
from pitch import freq_to_number, pitch_name

#AUDIO_FILE = "samples/alina.wav"
AUDIO_FILE = "samples/piano_c_major_scale.wav"
SCREEN_WIDTH = 1248
SCREEN_HEIGHT = 450
FPS = 30 #Frames fer Second
FFT_WINDOW_SECONDS = 0.5 # how many seconds of audio make up an FFT window sample

def load_audio_data(audio_file):
    sample_rate, data = io.wavfile.read(audio_file) # load the data

    print(f"Sample rate: {sample_rate}, type: {data.dtype}, duration: {len(data)/sample_rate}")

    if data.dtype == "int32":
        data = data.astype(np.float32) / (2**31)
    elif data.dtype == "int16":
        data = data.astype(np.float32) / (2**15)

    ch = np.array(data.T[0]) # this is a two channel soundtrack, get the first channel

    return sample_rate, data, ch

def extract_sample(audio_array, sample_rate, frame_number):
    '''Cuts audio into chunks / windows for the FFT to process. 
        It is not recommended to put all the data into FFT at once'''
    audio_length = len(audio_array)/sample_rate # seconds
    frame_count = int(audio_length*FPS) # how many 
    frame_interval = int(audio_length/frame_count) # data points
    fft_window_size = int(sample_rate * FFT_WINDOW_SECONDS) # data points

    begin = frame_number * frame_interval
    end = begin + fft_window_size

    return audio_array[begin:end]

#rfft_freq = np.fft.rfftfreq(fft_window_size, 1/sample_rate)

def play_tone(freq, time):
    buffer = np.sin(2 * np.pi * np.arange(44100*time) * freq / 44100).astype(np.float32)
    sound = pygame.mixer.Sound(buffer * 0.2)
    sound.play(0)

if __name__ == "__main__":
    pygame.mixer.init(frequency=44100, size=32, channels=2)
    pygame.init()
    pygame.display.set_caption('Alina PyPiano')
    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 30)
 
    sample_rate, audio_data, audio_channel = load_audio_data(AUDIO_FILE)
    sound = pygame.mixer.Sound(audio_data)
    sound.play(0)

    frame_step = (sample_rate / FPS) # audio samples per video frame
    fft_window_size = int(sample_rate * FFT_WINDOW_SECONDS) # data points
    audio_duration = int(len(audio_channel) / sample_rate)

    # Hanning Window function - see https://www.sciencedirect.com/topics/engineering/hanning-window
    window = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, fft_window_size, False)))

    for frame_number in range(audio_duration*FPS):
        sample = extract_sample(audio_channel, sample_rate, frame_number)

        fhat = np.fft.fft(sample * window)
        PSD = (fhat * np.conj(fhat) / fft_window_size).real

        freq = (sample_rate / fft_window_size) * np.arange(fft_window_size)

        PSD  = PSD[0:4200]
        freq = freq[0:4200]

        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html
        lst, _ = signal.find_peaks(PSD, height=0.5, distance=10)

        if len(lst):
            maxfreq_id = lst[0]
            maxfreq = freq[maxfreq_id]
            #play_tone(maxfreq, 1/4)

        # Draw in PyGame
        screen.fill((0,0,0))

        PSD_draw = 250-PSD*10
        freq_draw = freq * (SCREEN_WIDTH / len(freq))

        chart_data = np.vstack((freq_draw, PSD_draw)).T
        pygame.draw.aalines(screen, "lime", False, chart_data)

        for x in lst:
            pygame.draw.circle(screen, "blue", (freq_draw[x], PSD_draw[x]), 3, 2)
 
        active_notes = []
        for x in lst[0:1]:
            f = freq[x]
            n = freq_to_number(f)
            n0 = int(round(n))
            name = pitch_name(n0)
            active_notes.append(n0-21)
            #print(f"Frequency: {f} Hz, Number: {n0}, Note: {name}")
            label, lbl_rect = font.render(name, "white", size=16)
            screen.blit(label, (freq_draw[x], 260))

        piano = draw_piano((SCREEN_WIDTH, 150), active_notes)
        screen.blit(piano, (0, SCREEN_HEIGHT-150))

        #x_window_scale = width / len(window)
        #window_data = np.vstack((np.arange(len(window)) * x_window_scale, 250-window*250)).T
        #pygame.draw.aalines(screen, "white", False, window_data)

        # PyGame loop maintenance
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit(0)

        clock.tick(FPS)
