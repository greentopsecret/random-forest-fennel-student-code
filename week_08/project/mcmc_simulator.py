from supermarket import Supermarket
from clock import Clock
from customer_factory import CustomerFactory
import pandas as pd


class McmcSimulator:
    @staticmethod
    def run(
            matrix: pd.DataFrame,
            output_file: str,
            current_datetime: str = '2021-11-18 09:00:00',
            **kwargs
    ):
        clock = Clock(current_datetime)
        supermarket = Supermarket(clock, matrix.to_dict(orient='index'))
        customer_factory = CustomerFactory(clock, entrance_distribution=kwargs.get('entrance_distribution'))

        for i in range((21 - 7) * 60):
            customers = customer_factory.build_customer(Supermarket.get_first_section())
            for customer in customers:
                supermarket.add_customer(customer)

            supermarket.next_minute()

        # df = pd.DataFrame(data=output, columns=Supermarket.transitions_columns())
        # df.to_csv('./output/transitions.csv')

        f = open(output_file, 'w')
        f.write(supermarket.get_customer_transitions_csv(sep=';'))
        f.close()


if __name__ == '__main__':
    McmcSimulator.run(
        matrix=pd.read_csv('./output/transition_matrix.csv', index_col=0, sep=';'),
        output_file='./output/simulation.csv'
    )
