from typing import Type

import numpy as np
from clock import Clock
from week_08.clock import Clock


class Customer:
    """
    a single customer that moves through the supermarket
    in a MCMC simulation
    """
    _customer_no: int
    _location: str
    _active: bool
    _clock: Type[Clock]

    def __init__(self, customer_no: int, location: str, clock: Clock):
        self._customer_no = customer_no
        self._location = location
        self._active = True
        self._clock = clock

    def __repr__(self):
        return "%s;%d;%s" % (self._clock, self._customer_no, self._location)

    # def get_customer_no(self) -> int:
    #     return self._customer_no

    def set_location(self, location: str):
        self._location = location

    def get_location(self) -> str:
        return self._location

    def deactivate(self):
        self._active = False

    def is_active(self) -> bool:
        return self._active

    @staticmethod
    def get_next_location(probabilities: dict) -> str:
        np.random.choice(probabilities.keys, p=probabilities.values())
