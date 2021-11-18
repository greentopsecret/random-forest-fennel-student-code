from customer import Customer
from supermarket import Supermarket
from clock import Clock
import pandas as pd

if __name__ == '__main__':
    matrix = pd.read_csv('./output/transition_matrix.csv')

    clock = Clock(current_datetime='2021-11-18 09:00:00')

    customer1 = Customer(1, Supermarket.get_first_section(), clock)
    customer2 = Customer(2, Supermarket.get_first_section(), clock)
    customer3 = Customer(3, Supermarket.get_first_section(), clock)

    supermarket = Supermarket(clock, matrix.to_dict(orient='index'))
    supermarket.add_customer(customer1)
    supermarket.add_customer(customer2)
    supermarket.add_customer(customer3)

    for i in range(10):
        supermarket.next_minute()

    output = supermarket.get_customer_transitions_csv()
    pd.DataFrame(data=output, columns=Supermarket.transitions_columns())
    output.to_csv('./output/transitions.csv')
