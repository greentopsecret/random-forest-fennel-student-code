from typing import Callable

from customer import Customer
from clock import Clock


class CustomerFactory:
    _clock: Clock
    _callback: Callable[[Clock], int]

    def __init__(self, clock: Clock, **kwargs):
        entrance_distribution = kwargs.get('entrance_distribution')
        self._clock = clock
        self._callback = entrance_distribution if callable(entrance_distribution) else CustomerFactory._default_customer_dist
        self._last_customer_no = 0

    def build_customer(self, location: str) -> list[Customer]:
        cnt = self._callback(self._clock)
        for i in range(cnt):
            self._last_customer_no += 1
            yield Customer(self._last_customer_no, location, self._clock)

    @staticmethod
    def _default_customer_dist(clock: Clock) -> int:
        return 1
