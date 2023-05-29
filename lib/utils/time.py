'''
Module for utility time functions
'''
from datetime import datetime
from dateutil.parser import parse


def in_between(now: datetime, start: datetime, end: datetime) -> bool:
    '''
    Returns a bool if time is currently inbetween the specified start/end time parameters
    '''
    # In the event start/end not set, return false
    if not start and not end:
        return False
    if start <= end:
        return start <= now < end
    else:  # over midnight e.g., 23:30-04:15
        return start <= now or now < end


def parse_schedule_times(config: dict) -> tuple:
    '''
    Parses schedule.startTime and schedule.endTime from config.
    Returns a tuple of datetime objects.
    '''

    # Determine if we need to run on a schedule or not
    schedule = config.get('schedule', {})

    start_time = None
    if schedule.get('startTime'):
        start_time = parse(config['schedule']['startTime'])

    end_time = None
    if schedule.get('endTime'):
        end_time = parse(config['schedule']['endTime'])

    return (start_time, end_time)
