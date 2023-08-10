from _spinner_helper import Spinner
import pyaudiowpatch as pyaudio
import wave
import time, os

CHUNK_SIZE = 512

filename = "loopback_record.wav"

def capture_audio(duration: float = 5.0) -> str:
    try:
        # Capture audio using PyAudioWPatch
        # Return the audio data
        with pyaudio.PyAudio() as p, Spinner() as spinner:
            """
            Create PyAudio instance via context manager.
            Spinner is a helper class, for `pretty` output
            """
            try:
                # Get default WASAPI info
                wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            except OSError:
                spinner.print("Looks like WASAPI is not available on the system. Exiting...")
                spinner.stop()
                exit()
            
            # Get default WASAPI speakers
            default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

            if not default_speakers["isLoopbackDevice"]:
                for loopback in p.get_loopback_device_info_generator():
                    """
                    Try to find loopback device with same name(and [Loopback suffix]).
                    Unfortunately, this is the most adequate way at the moment.
                    """
                    if default_speakers["name"] in loopback["name"]:
                        default_speakers = loopback
                        break
                else:
                    spinner.print("Default loopback output device not found.\n\nRun `py -m pyaudiowpatch` to check available devices.\nExiting...\n")
                    spinner.stop()
                    exit()

            spinner.print(f"Recording from: ({default_speakers['index']}){default_speakers['name']}")
            
            wave_file = wave.open(filename, 'wb')
            wave_file.setnchannels(default_speakers["maxInputChannels"])
            wave_file.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
            wave_file.setframerate(int(default_speakers["defaultSampleRate"]))
            
            def callback(in_data, frame_count, time_info, status):
                """Write frames and return PA flag"""
                wave_file.writeframes(in_data)
                return (in_data, pyaudio.paContinue)
            
            with p.open(format=pyaudio.paInt16,
                    channels=default_speakers["maxInputChannels"],
                    rate=int(default_speakers["defaultSampleRate"]),
                    frames_per_buffer=CHUNK_SIZE,
                    input=True,
                    input_device_index=default_speakers["index"],
                    stream_callback=callback
            ) as stream:
                """
                Opena PA stream via context manager.
                After leaving the context, everything will
                be correctly closed(Stream, PyAudio manager)            
                """
                spinner.print(f"The next {duration} seconds will be written to {filename}")
                try:
                    time.sleep(duration) # Blocking execution while playing
                except KeyboardInterrupt:
                    spinner.print(f"Program interrupted by user. Exiting...")
                    spinner.stop()
                    exit()
            
            wave_file.close()
            return filename
    except KeyboardInterrupt:
        os.remove(filename)

#import speech_recognition as sr
import whisper

def recognize_speech(file: str, model_name: str = "tiny"):
    '''
    Recognize the speech in the audio data

    Return the recognized text

    Models: tiny, base, small, medium, large (.en for only english models - large doesn't have .en)

    Smaller models are faster, but less accurate
    '''

    '''
    https://www.thepythoncode.com/article/using-speech-recognition-to-convert-speech-to-text-python
    '''

    model = whisper.load_model(model_name)
    result = model.transcribe(file)
    return result["text"]