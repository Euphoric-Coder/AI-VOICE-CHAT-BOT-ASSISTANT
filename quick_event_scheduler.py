from pprint import pprint
from Google import Create_Service
import webbrowser
import datetime
from quick_response import quick_response
from time_detector import starting_time_recorder, ending_time_recorder
# from starting_time_extractor import starting_time_extractor
# from ending_time_extractor import ending_time_extractor

# import pyttsx3
CLIENT_SERVICE_FILE = "google_calendar_authenticator.json"
API_NAME = "calendar"
API_VERSION = "v3"
SCOPES = ["https://www.googleapis.com/auth/calendar"]
talker = pyttsx3.init()
talker.setProperty("rate", 200)


def audio_reciever(text):
    print(f"jarvis: {text}")
    talker.say(text)
    talker.runAndWait()


def quick_event_adder():
    audio_reciever(
        "Thank You for choosing the platform i can understand that you are in a hurry !!!!!!!"
    )
    audio_reciever(
        "But hope that you have atleast 1 to 2 minutes to hear the intructions!!!!! "
    )
    audio_reciever(
        "In this please try to tell only the title, starting time, ending time and the date of occurence of the event!!!!!!!! Thank You!!!!!  "
    )
    audio_reciever("Now starting the procedure !!!!!!")
    audio_reciever("Please state only  the summary for this event")
    summary = quick_response()
    if "title is " in summary:
        summary = summary.split("is ")[1]
    if "title will be " in summary:
        summary = summary.split("be ")[1]
    if "event will be " in summary:
        summary = summary.split("be ")[1]
    if "event is " in summary:
        summary = summary.split("is ")[1]
    if "store the the title as " in summary:
        summary = summary.split("as ")[1]
    audio_reciever(
        "Now please state the date of occurrence of the event!!!! In this please only specify the date of day and month!!!!!!1"
    )
    date = quick_response()
    audio_reciever("Now please state only the starting time")
    starting = quick_response()
    starting = starting_time_extractor(starting)
    audio_reciever("Now please state the ending time")
    ending = quick_response()
    ending = ending_time_extractor(ending)
    summary = summary.upper()
    t = summary + "on " + date + "at " + starting + " to " + ending
    ending = quick_response()
    print("The title of the event :" + summary)
    print("Date of occurrence :" + date)
    print("Starting time :" + starting)
    print("Ending Time :" + ending)
    """
    service=Create_Service(CLIENT_SERVICE_FILE,API_NAME,API_VERSION,SCOPES)
    calendar_id='hs3okg1cr3v8qumvunea1cn10o@group.calendar.google.com'
    created_event = service.events().quickAdd(
        calendarId='hs3okg1cr3v8qumvunea1cn10o@group.calendar.google.com',text=t).execute()
    webbrowser.open(created_event['htmlLink'])
    """
