from gtts import gTTS
import os

def speak(command):
    """
    This Function converts Text to Speech !!!
    Got the code or idea to have Text to Speech Capability from this website
    https://medium.com/@pelinokutan/how-to-convert-text-to-speech-with-python-using-the-gtts-library-dbe3d56730f1
    """
    # Initialize gTTS with the text to convert
    speech = gTTS(command)

    # Save the audio file to a temporary file
    speech_file = "speech.mp3"
    speech.save(speech_file)

    print("FRIDAY: " + command)
    # Play the audio file
    os.system("afplay " + speech_file)


if __name__ == "__main__":
    speak("Hello... I am AVA !!!! How are YOU today? I am very excited to be here!")
