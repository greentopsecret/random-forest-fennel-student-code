from typing import Callable
from supermarket import Supermarket
from clock import Clock
from customer_factory import CustomerFactory
import pandas as pd


def mcmc_simulate(
        matrix: pd.DataFrame,
        output_file: str,
        open_at: str = '2021-11-18 07:00:00',
        closed_at: str = '2021-11-18 22:00:00',
        customers_per_minute: Callable = None
):
    now = Clock(open_at)
    closed_at = Clock(closed_at)

    supermarket = Supermarket(matrix.to_dict(orient='index'))
    customer_factory = CustomerFactory(now, customers_per_minute=customers_per_minute)

    while now.less_than(closed_at):
        customers = customer_factory.build_customer(Supermarket.get_first_section())
        for customer in customers:
            supermarket.add_customer(customer)

        supermarket.next_minute()
        now.increment()

    with open(output_file, 'w', encoding='UTF-8') as file:
        file.write(supermarket.get_customer_transitions_csv(sep=';'))
        file.close()


if __name__ == '__main__':
    mcmc_simulate(
        matrix=pd.read_csv('./output/transition_matrix.csv', index_col=0, sep=';'),
        output_file='./output/simulation.csv'
    )
