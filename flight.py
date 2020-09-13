from datetime import datetime


class Flight:
    """
    A class which represents a flight information

    Attributes:
        is_valid (bool): shows whether the found flight is valid or not, default is True
        booking_token (str): token needs for validate the flight
        fly_from (str): departure location
        fly_to (str): arrival location
        price (int): price of flight
        dep_time (datetime): departure date and time
        arr_time (datetime): arrival date and time
    """

    def __init__(self, json_data):
        """
        The constructor for Flight class

        Parameters:
            json_data (dict): json from response data with all flight information
        """
        self.is_valid = True
        self.booking_token = json_data['booking_token']
        self.fly_from = json_data['cityCodeFrom']
        self.fly_to = json_data['cityCodeTo']
        self.price = json_data['price']
        self.dep_time = datetime.fromtimestamp(json_data['dTime'])
        self.arr_time = datetime.fromtimestamp(json_data['aTime'])

    @property
    def dep_date(self):
        """
        Returns:
            str: departure date of flight
        """
        return self.dep_time.date().strftime("%d/%m/%Y")

    @property
    def arr_date(self):
        """
        Returns:
            str: arrival date of flight
        """
        return self.arr_time.date().strftime("%d/%m/%Y")

    def __str__(self):
        return ' | '.join(['fly_from: ' + self.fly_from,
                           'fly_to: ' + self.fly_to,
                           'dep_time: ' + str(self.dep_time),
                           'arr_time: ' + str(self.arr_time),
                           'price: ' + str(self.price)])

    def __repr__(self):
        return self.__str__()
