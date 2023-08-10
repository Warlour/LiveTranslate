import functions

def main():
    while True:
        text = functions.recognize_speech(functions.capture_audio())
        if text:
            print(text)

    # if text:
    #     translation = translate_to_english(text)
    #     print(f"Original: {text}")
    #     print(f"Translation: {translation}", end="\n\n")
    #     # Display translation in UI if applicable

if __name__ == "__main__":
    main()