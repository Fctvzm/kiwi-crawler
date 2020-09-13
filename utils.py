from datetime import date, timedelta, datetime


def get_next_month(cur_date):
    """
    Get next month first date from current date

    Attributes:
         cur_date (datetime): current date
    Returns:
        datetime: next month first date
    """
    return cur_date.replace(year=cur_date.year + 1, month=1) \
        if cur_date.month == 12 \
        else cur_date.replace(month=cur_date.month + 1)


def get_date_range():
    """
    Get current and next month date for search params

    Returns:
        (str, str): tuple consists of current date and next month first date
    """
    cur_date = date.today()
    next_month_date = get_next_month(cur_date)
    return cur_date.strftime("%d/%m/%Y"), next_month_date.strftime("%d/%m/%Y")


def get_sleep_period():
    """
    Calculates left time until midnight

    Returns:
        float: time left until midnight
    """
    today = datetime.now()
    next_day = today + timedelta(days=1)
    midnight = next_day.replace(hour=0, minute=0, second=0)
    return (midnight - today).total_seconds()
