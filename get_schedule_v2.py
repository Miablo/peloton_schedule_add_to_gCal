import requests

import json
import google_cal_event_creator as _cal_creator
import datetime as _date_time
import google_cal_event_creator as event_creator
from dotenv import load_dotenv

import os

from enum import Enum as enum

"""
Created on Wed Sep 7 08:45PM 2022
Copyright 2022 Mio Diaz

"""

base_url = 'https://api.onepeloton.com'

load_dotenv()

USERNAME = os.environ.get('_username')
PASSWORD = os.environ.get('_password')
CAL_ID = os.environ.get('_cal_id')

class Emoji(enum):
    cycling = '🚴‍♀'
    meditation = '🧘‍♀️'
    strength = '🏋️‍♀️'
    cardio = '🥊'
    running = '🏃‍♀️'
    walking = '🚶‍♀️'
    yoga = '🧘'

def _peloton_session(s):
    '''
    _peloton_session
	Start peloton api session using username & password
	save the user id returned in the json data for usage
	later

    Parameters
    ----------
	s
        requests.Session()

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
    _get_reservations
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
        _get_ride_id(session, reservation['peloton_id'], headers)

    '''
    _get_ride_id
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
def _get_ride_id(session, reservation_id, headers):
    ride_url = base_url + '/api/peloton/' + reservation_id
    response = session.get(ride_url, headers=headers)
    rides = response.json()
    class_category = rides['live_class_category']
    if class_category != "":
        start_time = rides['scheduled_start_time']
    else:
        start_time = rides['pedaling_start_time']

    _get_ride_details(session, rides['ride_id'], headers, start_time)

    '''
    _get_ride_details
    Retrieves ride details using the ride_id passed from _get_ride_id
    in order to begin building calendar api response body properties
    Parameters
    ----------
    session
        session started in _peloton_session
    ride_id
        passed from _get_ride_id
    headers
        headers used for all calls asking for json
    '''
def _get_ride_details(session, ride_id, headers, start_time):
    ride_url = base_url + '/api/ride/' + ride_id + '/details'
    response = session.get(ride_url, headers=headers)
    rides = response.json()
    discipline = rides['ride']['fitness_discipline']
    duration = rides['ride']['duration']
    emoji = _get_emoji(rides['ride']['fitness_discipline'])
    summary = str(emoji) + ' ' + rides['ride']['title'] + ' ' + rides['ride']['instructor']['name']
    print(summary)
    start_time = _date_time.datetime.fromtimestamp(start_time)
    print(start_time)
    end_time = _get_end_time(start_time, duration)
    new_format = "%Y-%m-%dT%H:%M:%S-05:00"
    _cal_creator._calendar_api_call(summary, start_time.strftime(new_format), end_time.strftime(new_format), CAL_ID)

    '''
    _get_end_time
    Calculates end time of ride based on start time and duration

    Parameters
    ----------
    start_timestamp
        start time converted to datetime object
    duration
        duration of ride in seconds

    Returns
    ----------
    datetime object
        calculated end time of ride
    '''
def _get_end_time(start_timestamp, duration):
    return start_timestamp + _date_time.timedelta(seconds=duration)

    '''
    _get_emoji
    Selects appropriate emoji for calendar event summary based on fitness
    discipline of class
    Parameters
    ----------
    fitness_discipline
        string
    '''
def _get_emoji(fitness_discipline):
    match fitness_discipline:
        case 'cycling':
            return Emoji.cycling.value
        case 'cardio':
            return Emoji.cardio.value
        case 'meditation':
            return Emoji.meditation.value
        case 'strength':
            return Emoji.strength.value
        case 'running':
            return Emoji.running.value
        case 'walking':
            return Emoji.walking.value
        case _:
            print(" ")

    '''
    main method which asks for a session to start and stores the user id required
    for the next api call to get reservation ids
    '''
def main():
    s = requests.Session()
    usr_info = _peloton_session(s)
    usr_id = usr_info['user_id']

    headers = {
        "Content-Type": "application/json",
    }

    _get_reservations(s, usr_id, headers)



main()
