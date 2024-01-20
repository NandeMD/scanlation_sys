CREATE TABLE "series"
(
    id                integer not null
        constraint series_pk
            primary key autoincrement,
    name              text    not null,
    image_url         text default ':)',
    source_url        text    not null,
    base_url          text    not null,
    source_chap       real default 0,
    base_chap         real default 0,
    waiting_pr        real default 0,
    pred              real default 0,
    cleaned           real default 0,
    completed         real default 0,
    role_id           integer,
    channel_id        integer,
    discord_last_sent real,
    last_chapter_url  text default '',
    main_category     integer,
    current_category  integer,
    tl                integer,
    pr                integer,
    clnr              integer,
    tser              integer,
    qcer              integer,
    last_qced         real,
    drive_url         text,
    time2             text,
    time1             text,
    time_tl           text,
    time_pr           text,
    time_cln          text,
    time_ts           text,
    time_qc           text,
    last_readed       REAL,
    time_lr           TEXT,
    lr                INTEGER
)

