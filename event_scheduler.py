# import webbrowser
import time
import pytz
import datetime
from announcer import speak
from recorder import description_recorder, date_reciever
from date_retriever import date_interpreter
from time_detector import starting_time_recorder, ending_time_recorder

# from Google_authenticator import schedule_data as authenticate
# from announcer import record_audio
# from event_speaker import speak
# from date_reciever import date_reciever
# from starting_time_detector import digi_detector, pm_detector, am_detector
# from starting_time_recorder import recorder
# from start_time_values import min_return, hour
# from ending_time_detector import digi_detector1, pm_detector1, am_detector1
# from ending_time_recorder import recorder1
# from end_time_values import min_return1, hour1
# from pm_am_detector_sp import am_detector_sp, pm_detector_sp
# from updater import (
#     updater,
#     starting_date_updater,
#     ending_date_updater,
#     starting_time_updater,
#     ending_time_updater,
# )
# from date_time_combiner_with_timezone import date_time_combiner_with_timezone

TITLE = None
STARTING_DATE = None
ENDING_DATE = None
START_HOUR = None
END_HOUR = None
START_MINUTE = None
END_MINUTE = None
DESCRIPTION = None

denial_phrases = [
    "no",
    "not",
    "not at all",
    "skip",
    "don't",
    "don't want to",
    "prefer not to",
    "none",
    "nothing",
    "leave it blank",
    "negative",
    "refuse",
    "decline",
    "reject",
    "avoid",
    "ignore",
    "pass",
    "dismiss",
    "omit",
    "never",
    "won't",
    "nevermind",
    "nope",
    "nah",
    "I'd rather not",
    "nothing to add",
    "nothing more to say",
    "nothing to say",
    "nothing to provide",
    "not interested",
]


def update():
    pass


def title_prompter():
    """
    This funtion returns the title of the event through verbal instruction (i.e. voice) of the user
    """
    print(
        """
        Please mention the title of the event that you want to be held!!!!!!!! Also keep in mind that while saying the title of the event, you are requested to refrain yourself from using any other starting phrase other than the following:
        1. The title of the event is ........
        2. Title of the event will be ........
        3. The event will be about ........
        4. The event is about .......
        5. Store the title as ........
        6. The title is ......
        7. The title will be ........
        """
    )
    # Takes the audio from the user for the title of the event
    title = input("Enter title: ")
    # title = record_audio(n)
    # list of phrases that the user might use while telling the title
    user_phrase = [
        "the title of the event is",
        "title of the event will be",
        "the event will be about",
        "the event is about",
        "store the title as",
        "the title is",
        "the title will be",
    ]
    title = next(
        (title.replace(item, "") for item in user_phrase if title.startswith(item)),
        title,
    )
    if title == None or title == "":
        print(
            "Seems that you might have missed the title or there might be any issue in the system! Would again like to prompt for the title again ? [Answer in yes or no] "
        )
        consent = input("Enter consent: ")
        if not any(phrase in consent for phrase in denial_phrases):
            while title == "" or "Said Nothing":
                if title == "" or "Said Nothing":
                    speak(
                        "Seems that i did not get you quit well........ Please Repeat........."
                    )
                title = description_recorder()
            return title.strip().capitalize()
        else:
            return ""


def description_prompter():
    description = ""

    # Stores the list of denial phrases that could be used by the user to deny

    # Checks if any denial phrase or related word is present in the input
    speak(
        'Now Please state your consent if you want to have any description in the event or not?\n[Please Note: If you don\'t say anything or miss the answer will be taken as "no"]'
    )
    consent = description_recorder()
    if not any(phrase in consent for phrase in denial_phrases):
        while description == "" or "Said Nothing":
            if description == "" or "Said Nothing":
                speak(
                    "Seems that i did not get you quit well........ Please Repeat........."
                )
            description = description_recorder()
        return description.strip().capitalize()
    else:
        return ""


def date_time_combiner_with_timezone(year=2023, month=12, day=12, hour=12, minute=30):
    dt = datetime.datetime(year, month, day, hour, minute, 0)
    utc = pytz.timezone("Asia/Kolkata")
    dt = dt.astimezone(utc)
    return dt.isoformat()


def date_prompter(ch):
    # Variables to store two different types of phrases to be used while asking for starting date
    start_date_prompt_phrase_1 = "Now Please tell the date from when would you like the event named '' to be started or more precisely the starting date!\n[Please Note: The Date is a mandatory field that is, it needs to be given at any case to create the event]"
    start_date_prompt_phrase_2 = "Now Please tell the date from when would you like the event to be started or more precisely the starting date!\n[Please Note: The Date is a mandatory field that is, it needs to be given at any case to create the event]"

    # Variables to store two different types of phrases to be used while asking for ending date
    end_date_prompt_phrase_1 = f"Now Please tell the date from when would you like the event named {TITLE} to be ended or more precisely the endding date!\n[Please Note: The Ending Date if choosen to give is a mandatory field that is, it needs to be given at any case to create the event]"
    end_date_prompt_phrase_2 = "Now Please tell the date from when would you like the event to be ended or more precisely the ending date!\n[Please Note: The Ending Date if choosen to give is a mandatory is a mandatory field that is, it needs to be given at any case to create the event]"

    match ch:
        case 1:
            speak(
                start_date_prompt_phrase_2
                if TITLE == "" or TITLE is None
                else start_date_prompt_phrase_1
            )
            data = date_reciever("1")
            start_date = date_interpreter(data)
            while True:
                if start_date == None:
                    speak(
                        "It seems that you might have missed telling the date or I might not be able to hear the 'starting date'!!!!!!!!!"
                    )
                    speak(
                        "Starting procedure to reexecute the program............. Please wait for some moment starting reexecution as soon as possible"
                    )
                    speak(
                        "Reboot successfull starting the system......... System awakened........... "
                    )
                    speak("starting audio reciever...........")
                    speak("audio reciever started")
                    data = date_reciever("1")
                    start_date = date_interpreter(data)
                else:
                    speak(
                        'Thank You.........\nYour starting date "'
                        + str(start_date)
                        + '" is successfully added !'
                    )
                    break
            return start_date
        case _:
            speak(
                end_date_prompt_phrase_2
                if TITLE == "" or TITLE is None
                else end_date_prompt_phrase_1
            )
            end_date = date_interpreter(date_reciever("2"))
            while True:
                if end_date == None:
                    speak(
                        "It seems that you might have missed telling the date or I might not be able to hear the 'ending date'!!!!!!!!!"
                    )
                    speak(
                        "Starting procedure to reexecute the program............. Please wait for some moment starting reexecution as soon as possible..........Reboot successfull starting the system......... System awakened........... "
                    )
                    speak("starting Audio Reciever...........")
                    speak("Audio Reciever started")
                    end_date = date_interpreter(date_reciever("2"))
                else:
                    speak(
                        'Thank You.........\nYour ending date "'
                        + str(end_date)
                        + '" is successfully added !'
                    )
                    break
            return end_date


def add_event_details_verbally():
    global TITLE, DESCRIPTION, STARTING_DATE, ENDING_DATE, START_HOUR, START_MINUTE, END_HOUR, END_MINUTE
    TITLE = title_prompter()
    DESCRIPTION = description_prompter()
    STARTING_DATE = date_prompter(1)
    speak(
        "Appologies for disturbing you every time for the details!!!!!! But the details are necessary for the creation of the event. So in the circumstance, please co-operate!!!!!!!!!!!"
    )
    if TITLE != "" or None:
        speak(
            'Now please mention time from which you would like to start the event namely "'
            + TITLE
            + '" or more precisely state the starting time!!!!!!!!!'
        )
    else:
        speak(
            "Now please mention time from which you would like to start the event or more precisely state the starting time!!!!!!!!!"
        )

    speak(
        "One thing to note.......\nPlease be very specific about telling the time!!!!!!!!! please don't use commands other than 'the time will be ' or 'the time is'.\nThank You!"
    )
    START_HOUR, START_MINUTE = starting_time_recorder()

    speak(
        f"Do you want to extend this event further till any date i.e. do you want this event to extend more than one day that is more than {STARTING_DATE}\n[Please Note: Answer in either yes or no]"
    )
    consent = description_recorder()
    if not any(phrase in consent for phrase in denial_phrases):
        ENDING_DATE = date_prompter(2)
    else:
        speak("As you wish......Storing the Ending Date Same as Starting Date!")
        return STARTING_DATE

    if TITLE != "" or None:
        speak(
            'Now please mention time from which you would like to end the event namely "'
            + TITLE
            + '" or more precisely state the ending time!!!!!!!!!'
        )
    else:
        speak(
            "Now please mention time from which you would like to end the event or more precisely state the ending time!!!!!!!!!"
        )

    speak(
        "One thing to note.......\nPlease be very specific about telling the time!\nplease don't use commands other than 'the time will be ' or 'the time is'.\nThank You!"
    )
    END_HOUR, END_MINUTE = starting_time_recorder()
    speak(
        "Thank you !!!!! All the information is stored. Now check whether all the information are corect or not!!!!!"
    )
    speak(
        "You have been given 20 seconds of time so you can keep a track of the details given below please utilise the time to note if you want to update any of the details !!!!! Thank You"
    )
    print(
        f"""Title: {TITLE}\n
        Description: {DESCRIPTION}\n
        Starting Date: {STARTING_DATE}\n
        Ending Date: {ENDING_DATE}\n
        Starting Time: {START_HOUR}:{START_MINUTE}\n
        Ending Time: {END_HOUR}:{END_MINUTE}"""
    )

    time.sleep(20)

    speak(
        "Time over ............ now starting procedure to hear that whether updation of anything is required or not !!!!!!!!!!!!"
    )
    speak(
        """
      Please state that if you want to change any of the above datas as after this the system will input the data in the event of your Google Calendar!!!!!!!!
      """
    )
    speak("Now do you want to update or change anything !!!!!!!!!!!!")

    consent = description_recorder()
    if not any(phrase in consent for phrase in denial_phrases):
        speak(
            "Sure, Launching the Update Interface for updating the evene details........\nPlease bear with this as it might take some time........\nThank You! Starting Procedure........."
        )
        update()

    speak(
        "Ok then all the above data will be entered into your Google Calendar.............. THANK YOU for your kind co-operation!!!!!!!!"
    )

    EVENT_STARTDATETIME = date_time_combiner_with_timezone(
        STARTING_DATE.year,
        STARTING_DATE.month,
        STARTING_DATE.DAY,
        START_HOUR,
        START_MINUTE,
    )

    EVENT_ENDDATETIME = date_time_combiner_with_timezone(
        ENDING_DATE.year,
        ENDING_DATE.month,
        ENDING_DATE.DAY,
        END_HOUR,
        END_MINUTE,
    )


# #     service = authenticate()
# #     print(service)
# #     calendar_id = "hs3okg1cr3v8qumvunea1cn10o@group.calendar.google.com"
# #     event = {
# #         "title": title,
# #         "location": "new gitanjali, SN Roy Rd, Pathak Para, Behala, Kolkata, West Bengal 700034, India",
# #         "description": description,
# #         "start": {
# #             "dateTime": starting_datetime,
# #             "timeZone": "Asia/Kolkata",
# #         },
# #         "end": {"dateTime": ending_datettime, "timezone": "Asia/Kolkata"},
# #         "reminders": {
# #             "useDefault": False,
# #             "overrides": [
# #                 {"method": "email", "minutes": 24 * 60},
# #                 {"method": "popup", "minutes": 10},
# #                 {"method": "popup", "minutes": 5},
# #                 {"method": "email", "minutes": 1 * 60},
# #                 {"method": "email", "minutes": 2 * 60},
# #             ],
# #         },
# #     }
# #     event = service.events().insert(calendarId=calendar_id, body=event).execute()
# #     print("Event: '" + title + "' created!!!!!!!")
# #     speak(
# #         "Congratulations your event named '" + title + "' has been created !!!!!!!!!!"
# #     )
# #     speak(
# #         "Now opening the page in 'Google Calendar' where this event is stored!!!!!!!!!!!"
# #     )
# #     url = event.get("htmlLink")
# #     webbrowser.open(url)


# # event_creator("sagnik dey")
# event_creator("title of the event will be Tester")


def add_event_details_typed():
    pass


if __name__ == "__main__":
    # print(type(date_prompter(1)))
    # pass
    # event_creator()
    print(TITLE)
