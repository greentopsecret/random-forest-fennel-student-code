import datetime


class Clock:
    DELTA_IN_MINUTES = 1
    FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, current_datetime):
        """
        :param current_datetime: example '2021-11-18 09:00:00'
        """
        self.dt = datetime.datetime.strptime(current_datetime, Clock.FORMAT)

    def increment(self):
        self.dt = self.dt + datetime.timedelta(minutes=Clock.DELTA_IN_MINUTES)

    def __repr__(self) -> str:
        return self.dt.strftime(Clock.FORMAT)
