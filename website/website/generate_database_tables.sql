create table user
(
    id       integer not null
        constraint user_pk
            primary key autoincrement,
    email    text,
    password text,
    username text,
    role     text default 'normal'
);

create unique index main.user_email_uindex
    on main.user (email);

create unique index main.user_id_uindex
    on main.user (id);

create unique index main.user_username_uindex
    on main.user (username);

