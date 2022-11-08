from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os

def _calendar_api_call(summary, start_time, end_time, _cal_id):
    """

    """
    #start of google API code
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        # # Call the Calendar API
        _new_cal_event(service, summary, str(start_time), str(end_time),"America/New_York", _cal_id)
    except HttpError as error:
        print('An error occurred: %s' % error)

## https://developers.google.com/calendar/api/v3/reference
def _new_cal_event(service, summary, start_time, end_time, timezone, _cal_id):
    '''
    Creates event response body for calendar api post
    request used to add event to calendar and uses calendar
    service to insert event on selected calendar

    Parameters
    ----------
    service
        session
    summary
        string
    start_time
        datetime object
    end_time
        datetime object
    timezone
        string
    '''
    event = {
      'summary': summary,
      'start': {
        'dateTime': start_time,
        'timeZone': timezone,
      },
      'end': {
        'dateTime': end_time,
        'timeZone': timezone,
      },
    }

    event = service.events().insert(calendarId=_cal_id, body=event).execute()

    # with open('events.json', 'a') as token:
    #     if not _is_duplicate_event(str(token), event, service, _cal_id):
    #         token.writelines('%s\n' % (event.get('id')))
    #         event = service.events().insert(calendarId=_cal_id, body=event).execute()
    #         print('Event created: %s' % (event.get('htmlLink')))
    #     else:
    #         service.events().delete(calendarId=_cal_id, eventId=token).execute()

def _is_duplicate_event(token, event, service, _cal_id):
    with open('events.json', 'r') as r:
        summary = service.events().get(calendarId=_cal_id, eventId=str(r)).execute()
        if summary['summary'] == event:
            return True

    return False


