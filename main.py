from pydub import AudioSegment
import numpy as np
import scipy.fftpack
import pygame
import os

pygame.init()
pygame.mixer.init()

pygame.font.init()
font = pygame.font.SysFont('Times New Roman', 25)

screen_width = 16 * 70
screen_height = 9 * 70

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Music Visualizer")


# -------- Załadowanie pliku audio

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
    return np.clip(int(current_time / time_per_sample), 0, len(pitches) - 1)

def calculate_frequency_ranges(n, base=2, min_freq=20, max_freq=20000):
    # n - liczba interwałów, granic n + 1
    # matematyka : kazdy kolejny interwal jest 2x dluzszy od poprzedniego
    # zatem liczba najkrotszego odcinka bedzie sie zwiekszala wykladniczo wraz ze wzrostem n
    # wzor: int + 2int + 4int + 8int + ...
    # zatem bedzie to: 2^n - 1 interwalow

    result = []

    num_intervals = base**n - 1
    freq_length = max_freq - min_freq
    interval = freq_length / num_intervals      # dlugosc najkrotszego interwalu

    result.append(min_freq)
    for power in range(n):
        result.append(int(result[power] + interval * base**power))

    return result


print(calculate_frequency_ranges(10))


# --------------- KLASY ----------------

class SoundBar:
    def __init__(self, x, y, width, base_height):
        self.x = x
        self.y = y
        self.width = width
        
        self.base_height = base_height
        
        self.height = base_height
        self.target_height = base_height

        self.value = 100                    # procent wypelnienia
        self.frequency_range = (20, 20000)  # odbierane czestotliwosci

        self.speed = 1

        self.color = (100, 200, 60)

    def get_target_height(self):
        #pitches = values_list
        return np.clip(self.base_height + int(pitches[current_sample_index]), 0, screen_height)

    def change_height(self, multiplier=0.1):
        if self.height != self.target_height:
            diff = self.target_height - self.height
            self.height += diff * multiplier * self.speed
        return np.clip(np.abs(self.height), 1, 1000) * np.sign(self.height)

    def update(self):
        self.target_height = self.get_target_height()
        self.change_height()

    def draw(self):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.color, rect)


def create_ranged_audio_bars(n, start_x=10, lower_edge_y=screen_height, width=50, base_height=10, space=10):
    bars = []
    freq_ranges = calculate_frequency_ranges(n)

    for i in range(len(freq_ranges) - 1):
        bar = SoundBar(start_x + i * (space + width), 300, width, base_height)
        bar.frequency_range = (freq_ranges[i], freq_ranges[i + 1])

        bars.append(bar)

    return bars


base_height = 10


bars = create_ranged_audio_bars(10)





# bars = []    

# for i in range(10):
#     bars.append(SoundBar(20 + i * 30, screen_height - base_height, 50, 10))
#     color_val = int(255 * (i / 10))
#     color_val = np.clip(color_val, 0, 255)

#     color_val2 = np.clip(color_val + 50, 0, 255)
#     bars[i].color = (color_val, color_val, color_val2)




def change_height(current_height, target_height, speed, fraction=0.1):
    if current_height != target_height:
        diff = target_height - current_height
        current_height += diff * fraction * speed
    return np.clip(np.abs(current_height), 1, 1000) * np.sign(current_height)
    



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

print(len(pitches) == len(stft_result))

current_sample_index = 0

rect_height = 10
text_animation_counter = 0
was_enter_pressed = False

# ----------------------- MAIN LOOP ----------------------------------

running = True
while running and not quit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                was_enter_pressed = True

    elapsed_time_ms = pygame.mixer.music.get_pos()

    current_sample_index = np.clip(current_sample_index, 0, len(pitches))

    if current_sample_index < len(pitches):
        current_sample_index = get_current_sample_index(elapsed_time_ms, time_per_sample)

    if did_variable_change(old_sample_index, current_sample_index):
        #print(f'current_sample_index: {current_sample_index}')
        old_sample_index = current_sample_index


    import random

    # --------- Rysowanie ---------

    screen.fill((0, 0, 0))

    for bar in bars:
        bar.update()
        bar.draw()

    print(bars[0].target_height)

    #bars[0].x += random.randint(0, 1)


    #bar1.update()
    #bar1.draw()

    
    target_height = np.clip(10 + int(pitches[current_sample_index]), 0, screen_height)
    rect_height = 10 + change_height(rect_height, target_height, 2)

    rect_width = 50

    rect = pygame.Rect(screen_width / 2 - rect_width / 2, screen_height - rect_height, rect_width, rect_height)
    pygame.draw.rect(screen, (255, 0, 0), rect)


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

