# Import libraries
import os
from datetime import datetime, timedelta

import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define calendar ID (primary calendar by default)
calendar_id = 'primary'

# Set up authentication flow
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_credentials():
    creds = None
    client_secret_file_name = "token.json"
    if os.path.exists(client_secret_file_name):
        creds = Credentials.from_authorized_user_file(client_secret_file_name, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('external/credentials.json', SCOPES)
            creds = flow.run_local_server(port=51917)
        # Save credentials for future use
        with open(client_secret_file_name, 'w') as token:
            token.write(creds.to_json())
    return creds


# Build the service object
def create_event(event):
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)

    # Add event details
    event = {
        'summary': event['summary'],
        'start': {
            'dateTime': event['start_datetime'],
        },
        'end': {
            'dateTime': event['end_datetime'],
        },
    }

    # Insert event
    event = service.events().insert(calendarId=calendar_id, body=event).execute()

    if event.get("status") == "confirmed":
        return True, event.get('htmlLink')
    else:
        return False, None


def get_last_events():
    creds = get_credentials()

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        print("Getting the upcoming 10 events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    start_time = datetime.now(tz=pytz.timezone('Asia/Kolkata')).isoformat()
    end_time = (datetime.now(tz=pytz.timezone('Asia/Kolkata')) + timedelta(minutes=1)).isoformat()
    event = {
        'summary': 'Meeting',
        'start_datetime': start_time,  # Replace with desired start datetime (ISO 8601 format)
        'end_datetime': end_time,  # Replace with desired end datetime (ISO 8601 format)
    }
    # get_last_events()
    create_event(event)
