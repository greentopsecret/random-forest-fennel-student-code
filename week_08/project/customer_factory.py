from typing import Callable
from customer import Customer
from clock import Clock


class CustomerFactory:
    _clock: Clock
    _callback: Callable[[Clock], int]

    def __init__(self, clock: Clock, entrance_distribution: Callable = None):
        self._clock = clock
        self._last_customer_no = 0
        self._callback = entrance_distribution \
            if callable(entrance_distribution) \
            else CustomerFactory._default_customer_dist

    def build_customer(self, location: str) -> list[Customer]:
        cnt = self._callback(self._clock)
        for i in range(cnt):
            self._last_customer_no += 1
            yield Customer(self._last_customer_no, location, self._clock)

    @staticmethod
    def _default_customer_dist(clock: Clock) -> int:
        """method returns number of customers entering the store (per minute)"""
        return 1  # if this function is used then one customer will enter the store every minute
