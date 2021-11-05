## Second-hand-bikes pipeline
This pipeline monitors ebay-kleinanzeige.de website for second-hand bikes ads. For ads from Berlin it sends slack notifications.

![Pipeline diagram](./pipeline.svg)

### Components
* Crawler app - scrapes a website and stores data to NoSQL (MongoDB) database.
* Transformer app - incrementally pulls data from NoSQL database, transforms it and stores it to relational (Postgresql) database.
* Notifier app - incrementally pulls data from relational database and sends slack-notifications.

### Installation
1. 
```shell
# from the project folder 
cp .env.dist .env
```
2. set ENV variables values in `.env` file
3. Prepare databases
```shell
make mongodb_setup
make postgres_setup
```
4. Run applications
```shell
# in terminal 1
make crawler_running

# in terminal 2
make transformer_running

# in terminal 3
make notifier_running
```