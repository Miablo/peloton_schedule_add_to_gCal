import requests
import re as r
import peloton as Peloton
import json


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import time
import datetime as DateTime
from datetime import date

"""
Created on Wed Sep 7 08:45PM 2022
Copyright 2022 Mio Diaz

"""

base_url = 'https://api.onepeloton.com'

def _speloton_session(s):

	'''
	Start peloton api session using username & password
	save the user id returned in the json data for usage
	later

    Parameters
    ----------
	s
        session.request()

	Returns
    -------
    dict
        user id, session id, etc

	'''
	payload = {'username_or_email': USERNAME, 'password': PASSWORD} 
	headers = {
        "Content-Type": "application/json",
    }

	response = s.post(base_url + '/auth/login', json=payload, headers=headers)
	usr_info = response.json()

	return usr_info


def _get_reservations(session, usr_id, headers):

	'''
	Using the session started and the user id retrieved, get
	the reservations for this user - reservations = upcoming classes
	on the user's schedule - send each reservation id and get the 
	ride id

    Parameters
    ----------
	session  
		session started in _peloton_session
	usr_id   
		user id retrieved when session started
	headers  
		headers used for all calls asking for json content

	'''
	reservation_url = base_url + '/api/user/' + usr_id + '/reservations'
	    
	response = session.get(reservation_url, headers=headers)
	reservations = response.json()

	for reservation in reservations['data']:
		_get_ride_id(session, reservation['id'], headers)

def _get_ride_id(session, reservation_id, headers):

	'''
	Using the reservation id, get the ride id for the specified reservations
	use the ride id to retrieve ride details including instructor, description, etc

    Parameters
    ----------
	session 		
		session started in _peloton_session
	reservation_id  
		passed from _get_reservations
	headers 		
		headers used for all calls asking for json

	'''
	ride_url = base_url + '/api/peloton/' + reservation_id

	response = session.get(ride_url, headers=headers)
	rides = response.json()

	for ride in range(1):
		_get_ride_details(session, rides['ride_id'], headers)


def _get_ride_details(session, ride_id, headers):
	'''
	Retrieves ride details using the ride_id passed from _get_ride_id
	in order to begin building calendar api response body properties


    Parameters
    ----------
	session 		
		session started in _peloton_session
	reservation_id  
		passed from _get_reservations
	headers 		
		headers used for all calls asking for json

	'''
	ride_url = base_url + '/api/ride/' + ride_id + '/details'

	response = session.get(ride_url, headers=headers)
	rides = response.json()

	print(rides['ride']['description']) 
	print(rides['ride']['duration']) # returned in seconds
	print(rides['ride']['fitness_discipline']) # type of class (cycling, etc")
	print(rides['ride']['title']) # class title
	print(rides['ride']['instructor']['name'])
	print(rides['ride']['scheduled_start_time'])

	# event = {
 #      'summary': rides['ride']['description'],
 #      'start': {
 #        'dateTime': start_time,
 #        'timeZone': 'GMT-03:00',
 #      },
 #      'end': {
 #        'dateTime': end_time,
 #        'timeZone': 'GMT-03:00',
 #      },
 #      'recurrence': [
 #        'RRULE:FREQ=DAILY;COUNT=2'
 #      ],
 #      'reminders': {
 #        'useDefault': False,
 #        'overrides': [
 #          {'method': 'email', 'minutes': 24 * 60},
 #          {'method': 'popup', 'minutes': 10},
 #        ],
 #      },
 #    }


def _calendar_api_call(event_response_body):
    """

    """
    #start of google API code
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/calendar.events']
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
        # new_cal_event(service)
        # now = DateTime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        # print('Getting the upcoming 10 events')

        # events_result = service.events().list(calendarId='primary', timeMin=now,
        #                                       maxResults=10, singleEvents=True,
        #                                       orderBy='startTime').execute()
        # events = events_result.get('items', [])

        # if not events:
        #     print('No upcoming events found.')
        #     return

        # # Prints the start and name of the next 10 events
        # for event in events:
        #     start = event['start'].get('dateTime', event['start'].get('date'))
        #     print(start, event['summary'])

    except HttpError as error:
        print('An error occurred: %s' % error)

### TODO
## Research google api
## determine how build event for calendar event
## create function to pull duration of class and time of class to create end_time var
## determine what part will go into the event name ++ summary 
###
## https://developers.google.com/calendar/api/v3/reference
def _new_cal_event(service): 
    """


    """

    event = service.events().insert(calendarId='primary', body=event).execute()


def main():
	'''
	main method which asks for a session to start and stores the user id required
	for the next api call to get reservation ids 

	'''
	s = requests.Session()

	usr_info = _peloton_session(s)

	usr_id = usr_info['user_id']
	headers = {
        "Content-Type": "application/json",
    }

	_get_reservations(s, usr_id, headers)



main()
