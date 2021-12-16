FROM postgres:alpine3.14

#WORKDIR /tmp/
#COPY docker-entrypoint-initdb.d/postgres-setup.sql /tmp/
#RUN mkdir /docker-entrypoint-initdb.d

#ARG POSTGRES_USER
#ARG POSTGRES_DBNAME
# AWS stack is stuck in UPDATE_IN_PROGRESS because of the error FATAL: password authentication failed for user "postgres"
# TODO: figure out why does it happen
#COPY ./docker-entrypoint-initdb.d/postgres-setup.sh /docker-entrypoint-initdb.d/


# RUN #psql -h localhost -p 5432 -U ${POSTGRES_USER} -c "drop database if exists \"${POSTGRES_DBNAME}\"; create database \"${POSTGRES_DBNAME}\""
#	postgres psql -h localhost -p 5432 -U ${POSTGRES_USER} "${POSTGRES_DBNAME}" < /tmp/postgres-setup.sql