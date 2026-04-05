drop table if exists User;
drop table if exists Owner;
drop table if exists Customer;

-- CREATE TABLE post (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   author_id INTEGER NOT NULL,
--   created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--   title TEXT NOT NULL,
--   body TEXT NOT NULL,
--   FOREIGN KEY (author_id) REFERENCES user (id)
-- );
--

create table User (
    id       integer primary key autoincrement,
    username      text not null unique,
    password text not null
    -- the above is password hash actually
    -- created_at    timestamp default current_timestamp
);

create table Branch (
    id            integer primary key autoincrement,
    username      text not null unique,
    password text not null,
    name text not null unique,
    -- address       text,
    -- phone_number  text,
    -- opening_hour  text,
    -- closing_hour  text,
    -- location      text
);

-- create table tier (
--     tier_id   integer primary key autoincrement,
--     tier_name text not null
-- );
