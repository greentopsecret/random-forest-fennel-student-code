# from collections.abc import Callable
from typing import Callable
from clock import Clock

from customer import Customer
from week_08.clock import Clock


class CustomerFactory:
    _clock: Clock
    _callback: Callable[[Clock], int]

    def __init__(self, clock: Clock, callback: Callable):
        self._clock = clock
        self._callback = callback
        self._last_customer_no = 0

    def build_customer(self, location: str) -> list[Customer]:
        cnt = self._callback(self._clock)
        for i in range(cnt):
            self._last_customer_no += 1
            yield Customer(self._last_customer_no, location, self._clock)
