from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# SCOPES OF THE GOOGLE APIs
CALENDAR_SCOPE = ["https://www.googleapis.com/auth/calendar"]
GMAIL_SCOPES = "https://mail.google.com/"

def calendar():
    creds = None
    if os.path.exists("API DATA/Google_Calendar.pickle"):
        with open("API Data/Google_Calendar.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "API DATA/GOOGLE API.json", CALENDAR_SCOPE
            )
            creds = flow.run_local_server(port=0)

        with open("API DATA/Google_Calendar.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("calendar", "v3", credentials=creds)
    return service

def gmail():
    creds = None
    if os.path.exists("API DATA/Google_Gmail.pickle"):
        with open("API Data/Google_Gmail.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "API DATA/GOOGLE API.json", GMAIL_SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("API DATA/Google_Gmail.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("gmail", "v1", credentials=creds)
    return service

if __name__ == "__main__":
    calendar()
    gmail()
