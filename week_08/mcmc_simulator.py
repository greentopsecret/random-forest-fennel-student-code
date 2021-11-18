from supermarket import Supermarket
from clock import Clock
from customer_factory import CustomerFactory
import pandas as pd


def customer_dist(clock: Clock):
    return 1


if __name__ == '__main__':
    matrix = pd.read_csv('./output/transition_matrix.csv', index_col=0, sep=';')

    clock = Clock(current_datetime='2021-11-18 09:00:00')

    supermarket = Supermarket(clock, matrix.to_dict(orient='index'))
    customer_factory = CustomerFactory(clock, customer_dist)

    for i in range(10):
        customers = customer_factory.build_customer(Supermarket.get_first_section())
        for customer in customers:
            supermarket.add_customer(customer)

        supermarket.next_minute()

    # df = pd.DataFrame(data=output, columns=Supermarket.transitions_columns())
    # df.to_csv('./output/transitions.csv')

    output = supermarket.get_customer_transitions_csv(sep=';')
    f = open('./output/simulation.csv', 'w')
    f.write(output)
    f.close()
