import datetime


def is_valid_date(date):
    # Check if date is not in the past
    if date < datetime.date.today():
        return False
    else:
        return True


def convert_string_to_date(date):
    try:
        date.split("-")[0]
        date.split("-")[1]
        date.split("-")[2]
    except IndexError:
        return False

    try:
        date = date.split("-")
        day = int(date[0])
        month = int(date[1])
        year = int(date[2])
        date = datetime.date(year, month, day)
    except ValueError:
        return False
    return date


def convert_string_to_time(time):
    try:
        time.split(":")[0]
        time.split(":")[1]
    except IndexError:
        return False

    try:
        hour = int(time.split(":")[0])
        minute = int(time.split(":")[1])
        time = datetime.time(hour, minute)
    except ValueError:
        return False
    return time
