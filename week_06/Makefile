include .env
export

crawler_bash:
	docker-compose run crawler-app /bin/bash

transformer_bash:
	docker-compose run transformer-app /bin/bash

mock_bash:
	docker-compose run ebay-mock /bin/bash

mongodb_setup:
	docker-compose run crawler-app python /app/prepare-db.py

postgres_setup:
	echo "drop database if exists \"${POSTGRES_DBNAME}\"; create database \"${POSTGRES_DBNAME}\";" | docker-compose run postgres psql -h postgres -p 5432 -U ${POSTGRES_USER}
	docker-compose run postgres psql -h postgres -p 5432 -U ${POSTGRES_USER} "${POSTGRES_DBNAME}" < ./transformer-app/app/postgres-setup.sql

crawler_running:
	docker-compose run crawler-app python /app/app.py -vv

transformer_running:
	docker-compose run transformer-app python /app/app.py -vv