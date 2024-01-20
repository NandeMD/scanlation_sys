create table sr_series
(
    id           integer not null
        constraint id
            primary key autoincrement,
    serie_id     integer,
    serie_name   text,
    creator_id   integer not null,
    creator_name text    not null,
    created_at   integer not null,
    is_manga     integer not null,
    duration     integer not null,
    fee          real    not null
);

CREATE TABLE sr_works
(
    id integer not null
        constraint id
            primary key autoincrement
, creator_id integer not null, creator_name text not null, created_at integer not null, work_type integer not null, sr_id integer not null)

