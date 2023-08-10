import asyncio
import functions
import os

async def main():
    while True:
        # Capture audio asynchronously
        audio_future = asyncio.ensure_future(functions.capture_audio_async(2.0))

        # Start speech recognition asynchronously
        text = await functions.recognize_speech_async(audio_future)

        if text:
            print(text)

        # Display translation in UI if applicable

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Program interrupted by user. Exiting...")
        os.remove(functions.filename)