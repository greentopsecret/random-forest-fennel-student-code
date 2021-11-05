## Second-hand-bikes pipeline
This pipeline monitors ebay-kleinanzeige.de website for second-hand bikes ads. For ads from Berlin it sends slack notifications.

![Pipeline diagram](./pipeline.svg)

### Components
* [Crawler app](#Crawler-app) - scrapes a website and stores data to NoSQL (MongoDB) database.
* [Transformer app](#Transformer-app) - incrementally pulls data from NoSQL database, transforms it and stores it to relational (Postgresql) database.
* [Notifier app](#Notifier-app) - incrementally pulls data from relational database and sends slack-notifications.

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

## Crawler app
The app scrapes a website and stores data to NoSQL (MongoDB) database.
It scrapes all ads from the first `n` (by default 3) pages of the search. To ensure every ad is loaded only once there is an unique index in MongoDB.

## Transformer-app
Incrementally pulls new ads from MongoDB, transforms them and load to PostgreSQL.
To ensure that none ads are pulled from MongoDB twice there is a select query that checks what ad in PostgreSQL. 

## Notifier app
Incrementally pulls new ads from PostgreSQL and send them to slack.
It caches the last sent ad in a text file.
It also filters ads by title and price.