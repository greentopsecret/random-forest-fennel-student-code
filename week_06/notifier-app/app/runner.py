import schedule
import time
import logging

from src.App import App

if __name__ == '__main__':

    app = App()
    app.run()

    interval = 30
    schedule.every(interval).seconds.do(app.run)

    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            logging.error(str(e))
            time.sleep(5)
