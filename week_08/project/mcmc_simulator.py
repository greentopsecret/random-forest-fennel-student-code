from supermarket import Supermarket
from clock import Clock
from customer_factory import CustomerFactory
import pandas as pd
from typing import Callable


class McmcSimulator:
    @staticmethod
    def run(
            matrix: pd.DataFrame,
            output_file: str,
            current_datetime: str = '2021-11-18 07:00:00',
            entrance_distribution: Callable = None
    ):
        clock = Clock(current_datetime)
        supermarket = Supermarket(clock, matrix.to_dict(orient='index'))
        customer_factory = CustomerFactory(clock, entrance_distribution=entrance_distribution)

        for i in range((21 - 7) * 60):
            customers = customer_factory.build_customer(Supermarket.get_first_section())
            for customer in customers:
                supermarket.add_customer(customer)

            supermarket.next_minute()

        f = open(output_file, 'w')
        f.write(supermarket.get_customer_transitions_csv(sep=';'))
        f.close()


if __name__ == '__main__':
    def real_customers_distribution(clock: Clock) -> int:
        """

        :type clock: object that keeps current time
        """
        d = {
            7: 309,
            8: 458,
            9: 304,
            10: 286,
            11: 222,
            12: 250,
            13: 351,
            14: 330,
            15: 267,
            16: 348,
            17: 378,
            18: 443,
            19: 512,
            20: 331,
            21: 186
        }

        return int(d[clock.hour] / 120)


    McmcSimulator.run(
        matrix=pd.read_csv('./output/transition_matrix.csv', index_col=0, sep=';'),
        output_file='./output/simulation.csv',
        entrance_distribution=real_customers_distribution
    )
