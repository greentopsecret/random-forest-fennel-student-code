from datetime import datetime
from datetime import timedelta


class Clock:
    dt: datetime
    DELTA_IN_MINUTES = 1
    FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, current_datetime):
        """
        :param current_datetime: example '2021-11-18 09:00:00'
        """
        self.dt = datetime.strptime(current_datetime, Clock.FORMAT)

    def increment(self):
        self.dt = self.dt + timedelta(minutes=Clock.DELTA_IN_MINUTES)

    @property
    def hour(self) -> int:
        return self.dt.hour

    def __repr__(self) -> str:
        return self.dt.strftime(Clock.FORMAT)

    def less_than(self, dt2):
        return self.dt < dt2.dt
