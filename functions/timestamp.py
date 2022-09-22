from datetime import datetime


def time():
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    return current_time
