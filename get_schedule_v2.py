import requests
import re as r
import peloton as Peloton
import json

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
