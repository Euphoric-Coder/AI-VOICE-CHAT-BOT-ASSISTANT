from announcer import speak
from recorder import time_reciever
from datetime import datetime
import time


def extract_time(input_text):
    try:
        # Replace both "am" and "a.m." with the standard "am" format
        # Replace both "pm" and "p.m." with the standard "pm" format
        input_text = input_text.replace("a.m.", "am").replace("p.m.", "pm")

        # Parse the input text using datetime
        time = datetime.strptime(input_text, "%I:%M %p")

        # Extract hours and minutes
        hours = time.hour
        minutes = time.minute

        return hours, minutes
    except ValueError:
        # Handle the case where the input text is not in the expected format
        return None


def format_time(time):
    try:
        formatted_time, meridian = time.split()

        # If time is in 3 digits (e.g., 233), format it as HH:MM
        if len(formatted_time) == 3 and formatted_time.isdigit():
            formatted_time = formatted_time[0] + ":" + formatted_time[1:]

        # If time is in 1 digit (e.g., 2), format it as HH:00
        elif len(formatted_time) == 1 and formatted_time.isdigit():
            formatted_time += ":00"

        return f"{formatted_time} {meridian}"
    except:
        return None


def time_extractor(text):
    phrases = ["will be ", "is ", "take down the starting time as "]
    return format_time(
        next((text.split(phrase)[1] for phrase in phrases if phrase in text), text)
    )


def time_meridian_detector(text):
    try:
        if "p.m." in text or "pm" in text:
            return 1
        elif text.count("a.m.") or text.count("am") > 0:
            return 2
        else:
            return 0
    except:
        return None


def digit_detect(text):
    """
    Checks if there are any digit in the text or not
    """
    return (any(char.isdigit() for char in text)) if text != None else False


def starting_time_recorder():
    # Takes starting time as verbal input
    s_time = time_reciever(1)

    while True:
        s_time = time_extractor(s_time)
        c = time_meridian_detector(s_time)

        if (
            digit_detect(s_time) == 1
            and (c == 1 or c == 2 and c != None)
            and s_time is not None
        ):
            time.sleep(3)
            speak(
                f"Scanning Completed.............\nThank you your starting time '{s_time}' is being added!"
            )
            break

        speak(
            "Scanning completed............\nSeems that your starting time might not be recorded or you might have missed telling the starting time!!!!!\nStarting procedure to reboot the systems............ Please wait for some moment starting as soon as possible!!!"
        )
        s_time = time_reciever("1") if digit_detect(s_time) is not True else s_time

    return extract_time(s_time)


def ending_time_recorder():
    # Takes ending time as verbal input
    e_time = time_reciever()

    while True:
        e_time = time_extractor(e_time)
        c = time_meridian_detector(e_time)

        if (
            digit_detect(e_time) == 1
            and (c == 1 or c == 2 and c != None)
            and e_time is not None
        ):
            time.sleep(3)
            speak(
                f"Scanning Completed.............\nThank you your ending time '{e_time}' is being added!"
            )
            break

        speak(
            "Scanning completed............\nSeems that your ending time might not be recorded or you might have missed telling the ending time!!!!!\nending procedure to reboot the systems............ Please wait for some moment ending as soon as possible!!!"
        )
        e_time = time_reciever() if digit_detect(e_time) is not True else e_time

    return extract_time(e_time)
