import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGGING_FILE = os.path.join(BASE_DIR, 'debug.log')
OUTPUT_FILE = os.path.join(BASE_DIR, 'output.txt')

FLIGHT_DIRECTIONS = [
    ('ALA', 'TSE'),
    ('TSE', 'ALA'),
    ('ALA', 'MOW'),
    ('MOW', 'ALA'),
    ('ALA', 'CIT'),
    ('CIT', 'ALA'),
    ('TSE', 'MOW'),
    ('MOW', 'TSE'),
    ('TSE', 'LED'),
    ('LED', 'TSE')
]

# delay time after retry to check flight
DELAY_TIME = 10

# after amount of seconds to start checking flights
CHECK_FLIGHT_PERIOD = 900

# max concurrent tasks
MAX_TASKS = 30

FLIGHTS_POOL_NAME = 'https://api.skypicker.com'
SEARCH_FLIGHT_URL = FLIGHTS_POOL_NAME + '/flights?' \
                                        'fly_from={}&' \
                                        'fly_to={}&' \
                                        'date_from={}&' \
                                        'date_to={}&' \
                                        'sort=date&' \
                                        'partner=picky&' \
                                        'one_per_date=1'

CHECK_FLIGHTS = 'https://booking-api.skypicker.com'
CHECK_FLIGHT_URL = CHECK_FLIGHTS + '/api/v0.1/check_flights?' \
                                   'v=2&' \
                                   'booking_token={}&' \
                                   'bnum=1&' \
                                   'pnum=1&' \
                                   'affily=picky_kz'
