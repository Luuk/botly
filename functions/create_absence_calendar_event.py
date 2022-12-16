from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta


def create_absence_calendar_event(start_datetime, end_datetime, absent_user_email):
    try:
        service = build('calendar', 'v3', credentials=get_auth_token())

        event = {
            'summary': f"Afwezigheid {absent_user_email.split('@')[0].capitalize()}",
            'start': {
                'dateTime': datetime.strftime(start_datetime - timedelta(hours=1), "%Y-%m-%dT%H:%M:%S.%fZ"),
            },
            'end': {
                'dateTime': datetime.strftime(end_datetime - timedelta(hours=1), "%Y-%m-%dT%H:%M:%S.%fZ"),
            },
            'attendees': [
                {'email': absent_user_email},
            ]
        }

        event = service.events().insert(calendarId='primary', body=event).execute()

    except HttpError as error:
        print('An error occurred: %s' % error)


def get_auth_token():
    SCOPES = ['https://www.googleapis.com/auth/calendar.events']
    creds = None
    if os.path.exists('./config/google/token.json'):
        creds = Credentials.from_authorized_user_file('./config/google/token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                './config/google/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('./config/google/token.json', 'w') as token:
            token.write(creds.to_json())
    return creds
