#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  create table ads
  (
      index         serial primary key,
      incoming_id   varchar(25),
      provider      varchar(25),
      provider_id   varchar(50),
      title         varchar(255),
      "desc"        text,
      img           varchar(255),
      link          varchar(255),
      size          integer,
      floor         integer,
      rooms         numeric(2,1),
      price         integer,
      price_comment varchar(25),
      price_raw     varchar(25),
      location      varchar(255),
      location_zip  varchar(10),
      received_at   timestamp not null,
      transformed_at timestamp default now() not null
  );
  create unique index ads_provider_internal_id_uindex on ads (provider, provider_id);

  comment on column ads.incoming_id is 'PK from raw data (in NoSQL DB)';


create table search_requests
(
    id           serial primary key,
    chat_id      integer null,
    active       boolean default TRUE,
    price_max    integer,
    rooms_min    integer,
    size_min     integer,
    created_at   timestamp default now() not null,
    updated_at   timestamp default now() not null,
    UNIQUE(chat_id)
);

create table search_requests_zip
(
    id                   serial primary key,
    search_request_id    integer,
    zip                  integer,
    CONSTRAINT fk_search_requests
      FOREIGN KEY(search_request_id)
        REFERENCES search_requests(id),
    UNIQUE(search_request_id, zip)
);
EOSQL

