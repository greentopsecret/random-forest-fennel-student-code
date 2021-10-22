from model import Model
import pandas as pd
import argparse
import sys
import os


class ArtistPredictionCommand:

    def __init__(self):
        self.model = Model()

    def exec(self):
        args = ArtistPredictionCommand.__get_args()

        try:
            df = pd.read_csv(args.file, sep=',')
        except FileNotFoundError:
            sys.exit('File is not found. Did you forget to run scraper_command.py before? (filename = %s)' % args.file)

        self.model.fit(df['lyrics'], df['artist'])

        while True:
            fragment = input('Enter song fragment: ')
            prediction, prediction_probability = self.model.predict(fragment)
            print('Artist: %s' % prediction)
            print('Prediction probability: ', prediction_probability)
            continue_ = input('Do you want to continue? ("exit" for quit, "enter" for continue.) ')
            if continue_ == 'exit':
                print('Bye!')
                sys.exit(0)

    @staticmethod
    def __get_args():
        parser = argparse.ArgumentParser(
            description="Command that predicts artist by song fragment",
            epilog='Example of usage: python artist_prediction_command.py'
        )

        parser.add_argument('-v', '--verbose', help='verbose output', action='store_true')
        parser.add_argument(
            '-f',
            '--file',
            help='lyrics data file path',
            default=os.path.dirname(os.path.realpath(__file__)) + '/data/lyrics_data.csv'
        )

        return parser.parse_args()


if __name__ == '__main__':
    ArtistPredictionCommand().exec()
