from pydub import AudioSegment
import numpy as np
import scipy.fftpack
import os
import sys



def calculate_frequency_ranges(n, base=2, min_freq=20, max_freq=20000):
    result = []

    num_intervals = base**n - 1
    freq_length = max_freq - min_freq
    interval = freq_length / num_intervals      # dlugosc najkrotszego interwalu

    result.append(min_freq)
    for power in range(n):
        result.append(int(result[power] + interval * base**power))

    result[-1] = max_freq           # zapewniamy, ze ostatnia granica pokrywa sie z oryginalna

    return result



np.set_printoptions(threshold=sys.maxsize)

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

choice = 1

audio_file = folder_path + audio_files[choice]
audio = AudioSegment.from_mp3(audio_file)

#pygame.mixer.music.load(audio_file)
#pygame.mixer.music.play()

samples = np.array(audio.get_array_of_samples())

samples = samples[:len(samples)//1000]

#print(samples[:len(samples)//100])
#print('siema')

# STFT (Short-Time Fourier Transform)
def stft(samples, window_size, hop_size, sample_rate=44100):
    stft_result = []
    for i in range(0, len(samples) - window_size, hop_size):
        windowed_samples = samples[i:i + window_size] * np.hanning(window_size)
        fft_result = scipy.fftpack.fft(windowed_samples)
        stft_result.append(np.abs(fft_result[:window_size // 2]))
    return np.array(stft_result)


stft_result = stft(samples, 1024, 512)


#print(len(stft_result[2]))


def sum_amplitudes_in_frequency_ranges(spectrum, freq_ranges):
    num_ranges = len(freq_ranges) - 1
    result = [0] * num_ranges

    current_range = 0

    for i, amplitude in enumerate(spectrum):
        frequency = i * 44100 / 1024

        if frequency > freq_ranges[-1]:
            break

        if frequency > freq_ranges[current_range + 1]:
            current_range += 1

        result[current_range] += amplitude

    return result


def get_all_amplitudes(stft_result, freq_ranges):
    return [sum_amplitudes_in_frequency_ranges(spectrum, freq_ranges) for spectrum in stft_result]

freq_ranges = calculate_frequency_ranges(10)

print(freq_ranges)
print(sum_amplitudes_in_frequency_ranges(stft_result[2], freq_ranges))