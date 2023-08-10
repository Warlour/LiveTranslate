import asyncio
import functions
import os

async def main():
    files = ["file1.wav", "file2.wav"]
    # Capture first audio asynchronously
    n = 0
    print("Recording file1...")
    audio_future = asyncio.ensure_future(functions.capture_audio_async(files[n], 2.0))

    while True:
        n += 1

        # Start speech recognition asynchronously
        print(f"Transcribing file{1 - (n % 2) + 1} (index {1 - (n % 2)})")
        text = await functions.recognize_speech_async(files[n], audio_future)

        # Capture audio asynchronously
        print(f"Recording over file{(n % 2)+1} (index {n % 2})", end="\n\n")
        audio_future = asyncio.ensure_future(functions.capture_audio_async(files[(n % 2)], 2.0))

        

        if text:
            print(text)

        # Display translation in UI if applicable

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Program interrupted by user. Exiting...")
        for file in files:
            os.remove(file)