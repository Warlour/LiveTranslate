from _spinner_helper import Spinner
import pyaudiowpatch as pyaudio
import wave
import time

CHUNK_SIZE = 512

filename = "loopback_record.wav"

async def capture_audio_async(duration: float = 5.0) -> str:
    loop = asyncio.get_event_loop()

    # Use asyncio.to_thread() to run the blocking code in a separate thread
    def blocking_capture_audio():
        # Capture audio using PyAudioWPatch
        # Return the audio data
        with pyaudio.PyAudio() as p:
            """
            Create PyAudio instance via context manager.
            """
            try:
                # Get default WASAPI info
                wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            except OSError:
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
                    exit()
            
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
                try:
                    time.sleep(duration) # Blocking execution while playing
                except KeyboardInterrupt:
                    exit()
            
            wave_file.close()

    await asyncio.to_thread(blocking_capture_audio)

    return filename

#import speech_recognition as sr
import whisper
import asyncio

async def recognize_speech_async(audio_future, model_name: str = "tiny"):
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
    
    # Wait for the audio capture to complete before transcribing
    await audio_future

    result = model.transcribe(audio_future.result(), condition_on_previous_text=True)
    return result["text"]