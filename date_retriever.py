# from Google_authenticator import calendar_data as authenticate_google
import datetime

# import pytz
import time
from UTILITIES.announcer import speak

MONTHS = [
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENTIONS = ["rd", "th", "st", "nd"]


# def get_events(day, service):
#     date = datetime.datetime.combine(day, datetime.datetime.min.time())
#     end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
#     utc = pytz.UTC
#     date = date.astimezone(utc)
#     end_date = end_date.astimezone(utc)

#     events_result = (
#         service.events()
#         .list(
#             calendarId="primary",
#             timeMin=date.isoformat(),
#             timeMax=end_date.isoformat(),
#             singleEvents=True,
#             orderBy="startTime",
#         )
#         .execute()
#     )
#     events = events_result.get("items", [])
#     # NEW STUFF STARTS HERE
#     if not events:
#         speak("You have no upcoming events on this day")
#     else:
#         if len(events) > 1:
#             speak(f"You have {len(events)} events on this day.")
#         else:
#             speak(f"You have only {len(events)} event on this day")
#         for event in events:
#             meet = event["hangoutLink"]
#             zoom = event["description"]
#             zoom = zoom.split("Meeting ID: ")[1].split("\nPasscode")[0]
#             print(zoom)
#             zoom = event["description"]
#             zoom = zoom.split("Passcode: ")[1].split("\n")[0]
#             print(zoom)
#             start = event["start"].get("dateTime", event["start"].get("date"))
#             end = event["end"].get("dateTime", event["end"].get("date"))
#             try:
#                 start_time = str(start.split("T")[1].split("-")[0])
#                 if int(start_time.split(":")[0]) < 12:
#                     start_time = (
#                         str(int(start_time.split(":")[0]))
#                         + ":"
#                         + str(int(start_time.split(":")[1]))
#                     )
#                     start_time = start_time + " am"
#                 else:
#                     start_time = (
#                         str(int(start_time.split(":")[0]) - 12)
#                         + ":"
#                         + str(int(start_time.split(":")[1]))
#                     )
#                     start_time = start_time + " pm"
#                 end_time = str(end.split("T")[1].split("-")[0])
#                 if int(end_time.split(":")[0]) < 12:
#                     end_time = (
#                         str(int(end_time.split(":")[0]))
#                         + ":"
#                         + str(int(end_time.split(":")[1]))
#                     )
#                     end_time = end_time + " am"
#                     print(end_time)
#                 else:
#                     end_time = (
#                         str(int(end_time.split(":")[0]) - 12)
#                         + ":"
#                         + str(int(end_time.split(":")[1]))
#                     )
#                     end_time = end_time + " pm"
#                 print(event["summary"] + " at " + start_time)
#                 print("This event will be ending at " + end_time)
#                 speak(event["summary"] + " at " + start_time)
#                 speak("This event will be ending at " + end_time)
#             except:
#                 print(event["summary"])
#                 speak(event["summary"])


def date_interpreter(text):
    """
    This function returns the date as told by the user.
    For Example: if the user says, "Do i have anything on monday ?"
    It will return: YYYY-MM-DD (DD:- Being day of the current week's monday)
    """
    text = text.lower()

    # Stores current date i.e. today
    today = datetime.date.today()

    day_after_tomorrow = today + datetime.timedelta(days=1)
    if "today" in text:
        return today
    if "tomorrow" in text and "day after" not in text:
        return today + datetime.timedelta(days=1)
    if "yesterday" in text and "day before" not in text:
        return today - datetime.timedelta(days=1)
    if "day after tomorrow" in text:
        return day_after_tomorrow
    if "day before yesterday" in text:
        return today - datetime.timedelta(days=2)

    day, day_of_week, month, year = -1, -1, -1, today.year

    for word in text.split():
        # This loop is used to store all the data from the text to their respective variables (month, day_of_week, day, and year)
        if word in MONTHS:
            # Stores the month present in the text
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            # Stores the days of week present in the text
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            # If the date i.e. number of days is present in text
            day = int(word)
        else:
            # If a date is found with "th", "rd", "st", "nd" extensions then it is extracted by slicing
            for ext in DAY_EXTENTIONS:
                # Stores the index of the extension in the word
                index = word.find(ext)
                if index > 0:
                    try:
                        day = int(word[:index])
                    except ValueError:
                        pass
    if month < today.month and month != None:
        year = year + 1
    if month == None and day != -1:
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

    # In case a day of week is found on text
    if day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = (day_of_week - current_day_of_week + 7) % 7

        if text.count("next") >= 1:
            dif += 7 * text.count("next")

        return today + datetime.timedelta(days=dif)

    # In case of days only
    if day != -1:
        month = today.month if month == -1 else month
        return datetime.date(month=month, day=day, year=year)


def week_interpreter(text, date=datetime.date.today()):
    """
    This function returns date of the current day of week or next weeks.
    For Example: If the user says, "do i have anything next week?"
    It will return: YYYY-MM-DD (DD being the current day of week of the the next week) i.e.
    if today is 2023-12-11 then it will return 2023-12-18.
    """
    if "this" in text and "week" in text:
        return date
    if "next" in text and "week" in text:
        return date + datetime.timedelta(days=7)
    if "next to next" in text and "week" in text:
        return date + datetime.timedelta(days=14)
    if text.count("1st week") == 1:
        return date + datetime.timedelta(days=7)
    if text.count("2nd week") == 1:
        return date + datetime.timedelta(days=14)
    if text.count("3rd week") == 1:
        return date + datetime.timedelta(days=21)
    if text.count("4th week") == 1:
        return date + datetime.timedelta(days=28)


def execute(text):
    # SERVICE=authenticate_google()
    date = date_interpreter(text)
    date_for_week = week_interpreter(text)
    print(date, date_for_week)
    if date == None:
        # date=d
        pass
    # get_events(date,SERVICE)
    # print(date, date_for_week)


# execute("do i have anything on 2nd january last year")
execute("do i have anything on this week")
# execute(input("Enter the phrase: "))
