from pydub import AudioSegment
import numpy as np
import scipy.fftpack
import pygame

pygame.init()
pygame.mixer.init()

screen_width = 800
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Music Visualizer")


# -------- Załadowanie pliku audio

#audio_file = 'audio_files/18.mp3'
#audio_file = 'audio_files/test_audio.mp3'
audio_file = 'audio_files/test_audio2.mp3'
audio = AudioSegment.from_mp3(audio_file)

pygame.mixer.music.load(audio_file)
pygame.mixer.music.play()

samples = np.array(audio.get_array_of_samples())

# ------- Ustawienia samplowania
window_size = 1024
hop_size = 512

# STFT (Short-Time Fourier Transform)
def stft(samples, window_size, hop_size, sample_rate):
    stft_result = []
    for i in range(0, len(samples) - window_size, hop_size):
        windowed_samples = samples[i:i + window_size] * np.hanning(window_size)
        fft_result = scipy.fftpack.fft(windowed_samples)
        stft_result.append(np.abs(fft_result[:window_size // 2]))
    return np.array(stft_result)

# Obliczanie wysokosci tonu
def get_pitch(audio, stft_result, sample_rate, sampling_frequency=50):
    pitches = []
    audio_length = len(audio)
    num_secornds = np.floor(audio_length / 1000)
    samples_per_second = audio.frame_rate   
    stft_segments_per_second = np.floor(len(stft_result) / num_secornds)
    i = 0
    for spectrum in stft_result:
        #if i % stft_segments_per_second == 0:
        if i % sampling_frequency == 0:
            max_index = np.argmax(spectrum)
            frequency = max_index * sample_rate / window_size
            pitches.append(frequency)
        i += 1
    return pitches

# srednia wazona czestotliwosci
def weighted_average_of_freqs(list, sample_rate, window_size):
    result = []
    i = 0
    small_list_index = 0
    for small_list in list: # list to lista 2wymiarowa
        freq_sum = 0
        weights_sum = sum(small_list)
        for amplitude in small_list:
            frequency = small_list_index * sample_rate / window_size
            freq_sum += frequency * amplitude
            small_list_index += 1
        result.append(freq_sum / weights_sum)
        i += 1
    return result

def did_variable_change(old_value, new_value):
    return old_value != new_value

stft_result = stft(samples, window_size, hop_size, audio.frame_rate)

num_samples = len(stft_result)
audio_duration = len(audio)

# czas na jedna probke
time_per_sample = audio_duration / num_samples

def get_current_sample_index(current_time, time_per_sample):
    return int(current_time / time_per_sample)

quit = False

clock = pygame.time.Clock()

i = 0
fps = 60

current_frame = 0
time_per_frame = 1000 / fps

sample_counter = 0
sampling_frequency = 1

pitches = get_pitch(audio, stft_result, audio.frame_rate, sampling_frequency)
audio_duration2 = len(pitches) * sampling_frequency

old_sample_index = 0

# ----------------------- MAIN LOOP ----------------------------------

running = True
while running and not quit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    elapsed_time_ms = pygame.time.get_ticks()
    #elapsed_time_sec = elapsed_time_ms / 1000 

    seconds_clock = elapsed_time_ms
    if seconds_clock > 1000:
        seconds_clock = 0

    current_sample_index = get_current_sample_index(elapsed_time_ms, time_per_sample)
    if did_variable_change(old_sample_index, current_sample_index):
        print(f'current_sample_index: {current_sample_index}')
        old_sample_index = current_sample_index



    # --------- Rysowanie ---------

    screen.fill((0, 0, 0))

    rect_height = 10 + int(pitches[current_sample_index])
    rect_width = 50

    rect = pygame.Rect(screen_width / 2 - rect_width / 2, screen_height - rect_height, rect_width, rect_height)
    pygame.draw.rect(screen, (255, 0, 0), rect)


    # ----------------------------
    
    current_frame += 1
    if current_frame > fps:
        current_frame = 0

    sample_counter += 1
    if sample_counter > sampling_frequency:
        sample_counter = 0

    log_freq = 20 # every how many frames to log
    fraction_of_second = np.floor(current_frame / log_freq) / (fps / log_freq)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

