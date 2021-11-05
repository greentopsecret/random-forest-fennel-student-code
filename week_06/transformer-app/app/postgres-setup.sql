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
    price         integer,
    price_comment varchar(25),
    price_raw     varchar(25),
    location      varchar(255),
    location_zip  varchar(10),
    received_at   timestamp not null,
    transformed_at timestamp default now() not null
);
create unique index ads_provider_internal_id_uindex on ads (provider, provider_id);

comment on column ads.incoming_id is 'PK from raw data (in MongoDB)';