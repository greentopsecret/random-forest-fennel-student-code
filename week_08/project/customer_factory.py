from typing import Callable
from customer import Customer
from clock import Clock


class CustomerFactory:
    _clock: Clock
    _callback: Callable[[Clock], int]

    def __init__(self, clock: Clock, customers_per_minute: Callable = None):
        self._clock = clock
        self._last_customer_no = 0
        self._callback = customers_per_minute \
            if callable(customers_per_minute) \
            else CustomerFactory._default_customers_per_minute

    def build_customer(self, location: str) -> list[Customer]:
        cnt = self._callback(self._clock)
        for _ in range(cnt):
            self._last_customer_no += 1
            yield Customer(self._last_customer_no, location, self._clock)

    @staticmethod
    def _default_customers_per_minute(clock: Clock) -> int:
        """method returns number of customers entering the store (per minute)"""
        return 1  # if this function is used then one customer will enter the store every minute
