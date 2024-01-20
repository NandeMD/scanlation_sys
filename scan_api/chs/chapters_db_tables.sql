create table chapters
(
    id           INTEGER not null
        primary key autoincrement
        unique,
    serie_id     INTEGER not null,
    serie_name   TEXT    not null,
    chapter_num  REAL    not null,
    creator_id   INTEGER not null,
    creator_name TEXT    not null,
    created_at   REAL    not null,
    tl_id        INTEGER,
    tl_name      TEXT,
    tl_at        REAL,
    tl_bytes     INTEGER,
    pr_id        INTEGER,
    pr_name      TEXT,
    pr_at        REAL,
    clnr_id      INTEGER,
    clnr_name    TEXT,
    clnr_at      REAL,
    ts_id        INTEGER,
    ts_name      TEXT,
    ts_at        REAL,
    qc_id        INTEGER,
    qc_name      TEXT,
    qc_at        REAL,
    closer_id    INTEGER,
    closer_name  TEXT,
    closed_at    REAL,
    should_pred  integer,
    should_qced  integer
);

create table main.pay_periods
(
    id           INTEGER not null
        primary key autoincrement
        unique,
    creator_id   INTEGER not null,
    creator_name TEXT    not null,
    created_at   REAL    not null,
    closer_id    INTEGER,
    closer_name  TEXT,
    closed_at    REAL
);

