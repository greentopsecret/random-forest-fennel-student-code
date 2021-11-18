"""
Start with this to implement the supermarket simulator.
"""
from typing import List, Any

import numpy as np
import pandas as pd  # TODO: get rid of pandas here
from clock import Clock
from customer import Customer
from week_08.clock import Clock


class Supermarket:
    """manages multiple Customer instances that are currently in the market.
    """
    transitions: list[str]
    clock: Clock
    last_id: int
    minutes: int
    customers: list[Customer]
    probabilities_matrix: dict

    SECTIONS = (
        'entrance',
        'fruit',
        'checkout'
    )

    def __init__(self, clock: Clock, probabilities_matrix: dict):
        self.customers = []
        self.minutes = 0
        self.last_id = 0
        self.clock = clock
        self.transitions = []
        self.probabilities_matrix = probabilities_matrix

    @staticmethod
    def get_first_section() -> str:
        return Supermarket.SECTIONS[0]

    @staticmethod
    def get_last_section() -> str:
        return Supermarket.SECTIONS[len(Supermarket.SECTIONS) - 1]

    def __repr__(self):
        return 'not implemented :/'  # TODO: implement me

    #
    # def get_time(self):
    #     """current time in HH:MM format,
    #     """
    #     pass
    #
    # def print_customers(self):
    #     """print all customers with the current time and id in CSV format.
    #     """
    #     pass

    def next_minute(self):
        """propagates all customers to the next state.
        """

        for customer in self.customers:
            current_location = customer.get_location()

            # get next location
            p = self._get_location_probabilities(current_location)
            next_location = Customer.get_next_location(p)

            # handle location changing
            if next_location != current_location:
                self._store_transition(customer)
                customer.set_location(next_location)
                if next_location == Supermarket.get_last_section():
                    customer.deactivate()

        self._remove_inactive_customers()
        self.clock.increment()

    def add_customer(self, customer: Customer):
        self.customers.append(customer)

    def _remove_inactive_customers(self):
        """removes every customer that is not active any more.
        """
        self.customers = list(filter(lambda c: c.is_active(), self.customers))

    def _store_transition(self, customer: Customer):
        self.transitions.append(str(customer))

    def _get_location_probabilities(self, current_location: str) -> dict:
        return self.probabilities_matrix[current_location]

    # TODO: return list of transitions instead of csv
    def get_customer_transitions_csv(self, sep: str = ';') -> str:
        title = sep.join(['timestamp', 'customer_no', 'location'])
        lines = [title] + self.transitions
        return "\n".join(lines)
