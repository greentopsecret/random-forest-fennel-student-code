from datetime import datetime
from datetime import timedelta


class Clock:
    date_time: datetime
    DELTA_IN_MINUTES = 1
    FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, current_datetime):
        """
        :param current_datetime: example '2021-11-18 09:00:00'
        """
        self.date_time = datetime.strptime(current_datetime, Clock.FORMAT)

    def increment(self):
        self.date_time = self.date_time + timedelta(minutes=Clock.DELTA_IN_MINUTES)

    @property
    def hour(self) -> int:
        return self.date_time.hour

    def __repr__(self) -> str:
        return self.date_time.strftime(Clock.FORMAT)

    def less_than(self, dt2):
        return self.date_time < dt2.date_time
