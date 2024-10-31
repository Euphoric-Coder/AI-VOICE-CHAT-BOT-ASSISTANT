import speech_recognition as sr
from announcer import speak

r = sr.Recognizer()

def description_recorder():
    with sr.Microphone() as source:
        speak("I am listening!\nPlease speak up the description!")
        # speak(
        #     "Please note: Only tell the description and not anything as the system will read the other things as description!"
        # )
        audio = r.listen(source)
        voice_data = "Said Nothing"
        try:
            voice_data = r.recognize_google(audio)
            print(voice_data)
            speak("Thank you recieved the data!!!!!!!")
        except sr.UnknownValueError:
            speak("Sorry i did not get that")
        except sr.RequestError:
            speak("Sorry, my speech service is down")
        return voice_data.lower()


def date_reciever(n):
    with sr.Microphone() as source:
        if n == "1":
            speak(" I am Listening!!!!!! Please tell the starting date.....")
        if n == "2":
            speak(" I am Listening!!!!!! Please tell the ending date.....")
        if n == "3":
            speak("I am listening!!!!!! Please tell the updated starting date......")
        if n == "4":
            speak("I am listening!!!!!! Please tell the updated ending date.......")
        if n == "5":
            speak(
                "I am listening!!!!!! Please tell the date when the all-day event will be occurring"
            )
        audio = r.listen(source)
        voice_data = "Said Nothing !!!!!!!?????"
        try:
            voice_data = r.recognize_google(audio)
            print(voice_data)
            speak("Thank you recieved the data!!!!!!!")
            speak("Now scanning the data...........")
        except sr.UnknownValueError:
            speak("Sorry i did not get that")
        except sr.RequestError:
            speak("Sorry, my speech service is down")
        return voice_data.lower()

description_recorder()

def time_reciever(n=None):
    with sr.Microphone() as source:
        match n:
            case 1:
                speak("I am Listening!!!!!! Please tell the starting time.....")
            case _:
                speak("I am Listening!!!!!! Please tell the ending time.....")
        audio = r.listen(source)
        voice_data = "Said Nothing !!!!!!!?????"
        try:
            voice_data = r.recognize_google(audio)
            print(voice_data)
            speak("Thank you recieved the data!!!!!!!")
            speak("Now scanning the data...........")
        except sr.UnknownValueError:
            speak("Sorry i did not get that")
        except sr.RequestError:
            speak("Sorry, my speech service is down")
        return voice_data.lower()
