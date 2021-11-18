from customer import Customer
from clock import Clock


class Supermarket:
    """manages multiple Customer instances that are currently in the market.
    """
    SECTION_FIRST = 'entrance'
    SECTION_LAST = 'checkout'

    transitions: list[str]
    clock: Clock
    minutes: int
    customers: list[Customer]
    probabilities_matrix: dict

    def __init__(self, clock: Clock, probabilities_matrix: dict):
        self.customers = []
        self.clock = clock
        self.transitions = []
        self.probabilities_matrix = probabilities_matrix

    @staticmethod
    def get_first_section() -> str:
        return Supermarket.SECTION_FIRST

    @staticmethod
    def get_last_section() -> str:
        return Supermarket.SECTION_LAST

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
                customer.set_location(next_location)
                self._store_transition(customer)
                if next_location == Supermarket.get_last_section():
                    customer.deactivate()

        self._remove_inactive_customers()
        self.clock.increment()

    def add_customer(self, customer: Customer):
        self.customers.append(customer)

    def _remove_inactive_customers(self):
        """removes every customer that is not active anymore
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
