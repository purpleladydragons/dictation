import pvporcupine
from pvrecorder import PvRecorder
from dotenv import load_dotenv
import os

load_dotenv()
# AccessKey obtained from Picovoice Console (https://console.picovoice.ai/)
access_key = os.getenv('PORCUPINE_API_KEY')


def listen_for_wakeword():
    handle = pvporcupine.create(access_key=access_key, keywords=['porcupine'])

    recorder = PvRecorder(
        device_index=-1,
        frame_length=handle.frame_length)
    recorder.start()

    print('waiting...')
    try:
        while True:
            pcm = recorder.read()
            result = handle.process(pcm)

            if result >= 0:
                return True
    except KeyboardInterrupt:
        print('quit')
    finally:
        recorder.delete()
        handle.delete()
        return False
