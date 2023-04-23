import subprocess
import pyaudio
import wave
from gpt import prompt_gpt
from wakeword import listen_for_wakeword
import numpy as np
import time
from collections import deque

SILENCE_THRESHOLD = 200
SILENCE_DURATION = 2
frames = deque()
silence_start_time = None

def callback(in_data, frame_count, time_info, status):
    global silence_start_time
    audio_data = np.frombuffer(in_data, dtype=np.int16)
    frames.append(audio_data.tobytes())
    if np.abs(audio_data).mean() < SILENCE_THRESHOLD:
        # Check if this is the start of silence
        if silence_start_time is None:
            silence_start_time = time.time()
        # Calculate the duration of silence
        silence_duration = time.time() - silence_start_time
        # Check if the duration of silence has reached the threshold
        if silence_duration >= SILENCE_DURATION:
            print("Silence detected for 2 seconds. Stopping recording.")
            return (in_data, pyaudio.paComplete)
    else:
        silence_start_time = None

    return (in_data, pyaudio.paContinue)

def record_audio():
    # Set the parameters for the recording
    FORMAT = pyaudio.paInt16  # Sample format
    CHANNELS = 1  # Mono
    RATE = 16000  # Sample rate (Hz)
    CHUNK = 1024  # Buffer size (in samples)
    # TODO obv biggest improvement is flexible recording duration...
    RECORD_SECONDS = 10  # Duration of recording (seconds)
    OUTPUT_FILENAME = "output.wav"  # Output file name

    # Create a PyAudio object
    p = pyaudio.PyAudio()

    # Open a streaming stream for recording
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    stream_callback=callback)

    # Start recording
    print("Recording...")

    while stream.is_active():
        time.sleep(0.01)

    # Stop the stream
    stream.stop_stream()
    stream.close()

    print('done recording')

    # Terminate the PyAudio object
    p.terminate()

    # Save the recorded data to a WAV file
    wf = wave.open(OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print("Audio saved to", OUTPUT_FILENAME)


def whisper(filename):
    cmd = f"/Users/austinsteady/code/whisper.cpp/main -m /Users/austinsteady/code/whisper.cpp/models/ggml-base.en.bin -f {filename} --no-timestamps"
    x = subprocess.run(cmd, shell=True, text=True, capture_output=True).stdout
    return x


def sanitize_transciption(text):
    text = text.replace('[BLANK AUDIO]', '')
    lines = text.split('\n')

    deduped = [lines[0]]
    for line in lines[1:]:
        if line != deduped[-1]:
            deduped.append(line)

    return '\n'.join(deduped)


def tts(text):
    subprocess.run(f"say " + text, shell=True)


while True:
    listen_for_wakeword()
    print('wakeword detected!')
    record_audio()
    speech = whisper('output.wav')
    print('raw', speech)
    sanitized = sanitize_transciption(speech)
    print('sani', sanitized)
    resp = prompt_gpt(sanitized, model='gpt-3.5-turbo')
    tts(resp)
    print('>>> ' + sanitized)
    print('<<< ' + resp)
