import asyncio
import aiohttp
import aiofiles
import json
import logging
import signal
import sys

import utils
import configs
from flight import Flight

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    datefmt="%H:%M:%S",
    filename=configs.LOGGING_FILE,
    level=logging.DEBUG
)
logger = logging.getLogger('search_flight')


async def shutdown(sig, event_loop):
    """
    Cancel all coroutines after killing process by signal and stop the event loop

    Attributes:
        sig (enum): type of signal
        event_loop: event loop that run asynchronous tasks and callbacks
    """
    logger.info('Received exit signal {}'.format(sig.name))
    tasks = [t for t in asyncio.Task.all_tasks() if t is not
             asyncio.tasks.Task.current_task()]
    for task in tasks:
        task.cancel()
    logger.info('Cancelling {} outstanding tasks'.format(tasks))
    results = await asyncio.gather(*tasks, return_exceptions=True)
    logger.info('Finished awaiting cancelled tasks, results: {}'.format(results))
    event_loop.stop()


class Crawler:
    """
    Web Crawler periodically search flights from Kiwi Api and validates them.

    Attributes:
        session (ClientSession): interface for making HTTP requests
        semaphore (Semaphore): allow us to protect resources from being overused
        flights (dict): contains all found flights, where key is combination of fly_from, fly_to, dep_date
        date_from (str): search flights from this date (dd/mm/YYYY) which is current day
        date_to (str): search flights upto this date (dd/mm/YYYY) which is next month first day
        flight_directions (list): list of need to search flight directions
    """

    def __init__(self, session):
        """
        The constructor for Flight class
        """
        self.session = session
        self.semaphore = asyncio.Semaphore(configs.MAX_TASKS)
        self.flights = {}
        self.date_from, self.date_to = utils.get_date_range()
        self.flight_directions = configs.FLIGHT_DIRECTIONS

    async def send_request(self, url):
        """
        Send GET request and converts response data to dict

        Attributes:
            url (str) : url where need to send get request
        Returns:
            dict: response data where all found flight information
        """
        try:
            response = await self.session.request(method='GET', url=url)
            response.raise_for_status()
            logger.info("Got response [%s] for URL: %s", response.status, url)
            data = await response.read()
            return json.loads(data)

        except aiohttp.ClientError as e:
            logger.error(
                "aiohttp exception for %s [%s]: %s",
                url,
                getattr(e, "status", None),
                getattr(e, "message", None),
            )

    async def search_flight(self, fly_from, fly_to, date_from, date_to):
        """
        Search flight with specific parameters and store in flights dict
        (the cheapest flight for one particular day)

        Attributes:
            fly_from (str): departure place
            fly_to (str): destination
            date_from (str): departure date
            date_to (str): arrival date
        """
        search_url = configs.SEARCH_FLIGHT_URL.format(fly_from, fly_to,
                                                      date_from, date_to)
        response_data = await self.send_request(search_url)
        for json_data in response_data['data']:
            flight = Flight(json_data)
            key = '-'.join([flight.fly_from, flight.fly_to, str(flight.dep_date)])
            if key in self.flights and self.flights[key].is_valid and \
                    self.flights[key].price < flight.price:
                continue
            self.flights[key] = flight

    async def check_flight(self, flight):
        """
        Validate found flight and search new one in case of invalid flight
        or change price with new price

        Attributes:
            flight (Flight): instance of class Flight
        """
        check_url = configs.CHECK_FLIGHT_URL.format(flight.booking_token)
        retries = 0
        while True:
            async with self.semaphore:
                data = await self.send_request(check_url)
            if data['flights_checked']:
                break
            retries += 1
            await asyncio.sleep(configs.DELAY_TIME * retries)

        if data['flights_invalid']:
            flight.is_valid = False
            await self.search_flight(flight.fly_from, flight.fly_to,
                                     flight.dep_date, flight.arr_date)
        elif data['price_change']:
            flight.price = data['total']

    async def check_flights_periodically(self):
        """
        Periodically after CHECK_FLIGHT_PERIOD seconds checks flights
        """
        while True:
            tasks = [self.check_flight(flight) for flight in self.flights.values()]
            await asyncio.gather(*tasks)

            logger.info('Checked number of %d flights', len(tasks))
            await self.write_to_file()
            await asyncio.sleep(configs.CHECK_FLIGHT_PERIOD)

    async def write_to_file(self):
        """
        Write the found flights to file
        """
        async with aiofiles.open(configs.OUTPUT_FILE, "w") as f:
            for value in self.flights.values():
                await f.write(str(value) + '\n')
            logger.info('Wrote results to file')

    async def search_flights_periodically(self):
        """
        Periodically at midnight updates flights and writes results to output file
        """
        while True:
            self.flights = {}
            self.date_from, self.date_to = utils.get_date_range()
            tasks = [self.search_flight(flight_dir[0], flight_dir[1],
                                        self.date_from, self.date_to)
                     for flight_dir in self.flight_directions]
            await asyncio.gather(*tasks)

            logger.info('Found %d flights for given directions', len(self.flights))
            await self.write_to_file()
            sleep_period = utils.get_sleep_period()
            await asyncio.sleep(sleep_period)

    def print_found_flights(self):
        """
        Prints current found flights
        """
        for value in self.flights.values():
            print('-' * 40 + '\n' + str(value))


async def main():
    """
    Initialize crawler and start coroutines
    """
    async with aiohttp.ClientSession() as session:
        crawler = Crawler(session)
        await asyncio.gather(*[crawler.search_flights_periodically(),
                               crawler.check_flights_periodically()])


if __name__ == '__main__':
    assert sys.version_info >= (3, 6), 'Script requires Python 3.6+.'

    loop = asyncio.get_event_loop()

    # types of signal need to listen in order to properly shutdown
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(s, lambda s=s: asyncio.ensure_future(shutdown(s, loop)))

    asyncio.ensure_future(main())
    try:
        loop.run_forever()
    finally:
        loop.close()
