from pydub import AudioSegment
import numpy as np
import scipy.fftpack
import pygame
import os
import sys
from stft import *

pygame.init()
pygame.mixer.init()

pygame.font.init()
font = pygame.font.SysFont('Times New Roman', 25)

screen_width = 16 * 70
screen_height = 9 * 70

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Music Visualizer")


# -------- Załadowanie pliku audio

def get_number_of_files_from_folder(folder_path):
    return len(os.listdir(folder_path))


def load_audio_files_from_folder(folder_path):
    files_and_folders = os.listdir(folder_path)
    audio_files = []
    for item in files_and_folders:
        if item.endswith('.mp3'):
            audio_files.append(item)
    return audio_files

folder_path = 'audio_files/'

audio_files = load_audio_files_from_folder(folder_path)



# ----------- Wybór pliku audio ------------

choice = 2

audio_file = folder_path + audio_files[choice]
audio = AudioSegment.from_mp3(audio_file)

pygame.mixer.music.load(audio_file)
pygame.mixer.music.play()

samples = np.array(audio.get_array_of_samples())


# ------- Ustawienia samplowania
window_size = 1024
hop_size = 512

# ------------- Przydatne funkcje ---------------




def did_variable_change(old_value, new_value):
    return old_value != new_value


NUM_BARS = 10


stft_result = stft(samples, window_size, hop_size, audio.frame_rate)

freq_ranges = calculate_frequency_ranges(NUM_BARS)

all_amplitudes = get_all_amplitudes(stft_result, freq_ranges)

print('done')

#quit = True







# --------------- KLASY ----------------

class SoundBar:
    def __init__(self, x, y, width, base_height):
        self.x = x
        self.y = y
        self.width = width
        self.lower_edge_y = y + base_height
        
        self.base_height = base_height
        
        self.height = base_height
        self.target_height = base_height

        self.value = 100                    # procent wypelnienia
        self.frequency_range = (20, 20000)  # odbierane czestotliwosci

        self.speed = 1

        self.color = (100, 200, 60)

        self.current_amp = 0

    
    def get_target_height(self):
        #pitches = values_list
        return np.clip(self.base_height + int(self.current_amp) * 0.1, 0, screen_height)

    def change_height(self, multiplier=0.1):
        if self.height != self.target_height:
            diff = self.target_height - self.height
            self.height += diff * multiplier * self.speed
        return np.clip(np.abs(self.height), 1, 1000) * np.sign(self.height)

    def update(self):
        self.target_height = self.get_target_height()
        self.change_height()

    def draw(self):
        rect = pygame.Rect(self.x, self.y - self.height, self.width, self.height)
        pygame.draw.rect(screen, self.color, rect)


import random

def get_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def create_ranged_audio_bars(n, start_x=10, lower_edge_y=screen_height, width=50, base_height=10, space=10):
    bars = []
    freq_ranges = calculate_frequency_ranges(n)

    for i in range(len(freq_ranges) - 1):
        bar = SoundBar(start_x + i * (space + width), 300, width, base_height)
        bar.frequency_range = (freq_ranges[i], freq_ranges[i + 1])
        bar.color = get_random_color()

        bars.append(bar)

    return bars


base_height = 10



bars = create_ranged_audio_bars(NUM_BARS)

clock = pygame.time.Clock()

i = 0
fps = 60

current_frame = 0
time_per_frame = 1000 / fps

sample_counter = 0
sampling_frequency = 1

#pitches = get_pitch(audio, stft_result, audio.frame_rate, sampling_frequency)
#audio_duration2 = len(pitches) * sampling_frequency

old_sample_index = 0

#print(len(pitches) == len(stft_result))

current_sample_index = 0

rect_height = 10
text_animation_counter = 0
was_enter_pressed = False


#freq_ranges = calculate_frequency_ranges(num_bars)


num_samples = len(stft_result)
audio_duration = len(audio)

# czas na jedna probke
time_per_sample = audio_duration / num_samples

def get_current_sample_index(current_time, time_per_sample):
    return np.clip(int(current_time / time_per_sample), 0, 1000 - 1)



# ----------------------- MAIN LOOP ----------------------------------

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                was_enter_pressed = True

    elapsed_time_ms = pygame.mixer.music.get_pos()

    current_sample_index = np.clip(current_sample_index, 0, 1000)

    if current_sample_index < 1000:
        current_sample_index = get_current_sample_index(elapsed_time_ms, time_per_sample)

    if did_variable_change(old_sample_index, current_sample_index):
        #print(f'current_sample_index: {current_sample_index}')
        old_sample_index = current_sample_index


    #print(current_sample_index)
    print(sum(all_amplitudes[current_sample_index]))


    import random

    # --------- Rysowanie ---------

    screen.fill((0, 0, 0))

    #amp_sum_single_list = big_sum[current_sample_index]
    for i in range(10):
        #bars[i].current_amp = amp_sum_single_list[i]

        bars[i].update()
        bars[i].draw()

        #print(bars[1].current_amp)



    if was_enter_pressed:
        text_animation_counter += 1

    def animation_function(x, multiplier=0.05):
        return x ** 2 * multiplier

    text_x = 10 + animation_function(text_animation_counter)

    text_surface = font.render(f'Now playing: {audio_files[choice]}', True, (255, 255, 255))
    screen.blit(text_surface, (text_x, 10))
    


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

