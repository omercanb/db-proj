drop table if exists User;
drop table if exists Owner;
drop table if exists Customer;
drop table if exists Store;
drop table if exists 'Table';
drop table if exists Game;
drop table if exists GameCopy;
drop table if exists Session;
drop table if exists SessionGameCopy;

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

create table Store (
    id            integer primary key autoincrement,
    username      text not null unique,
    password text not null,
    name text not null unique
    -- address       text,
    -- phone_number  text,
    -- opening_hour  text,
    -- closing_hour  text,
    -- location      text
);

create table 'Table' (
    store_id integer not null,
    table_num integer not null,
    capacity integer,
    foreign key (store_id) references Store(id),
    primary key (store_id, table_num)
);

create table Game (
    id integer primary key autoincrement,
    name text not null unique
);

create table GameCopy (
    game_id integer not null,
    store_id integer not null,
    copy_num integer not null,
    foreign key (game_id) references Game(id),
    foreign key (store_id) references Store(id),
    primary key (game_id, store_id, copy_num)
);

create table Session (
    id integer primary key autoincrement,
    user_id integer not null,
    store_id integer not null,
    table_num integer not null,
    day text not null,
    start_time integer not null,
    end_time integer not null,
    foreign key (store_id, table_num) references 'Table'(store_id, table_num),
    foreign key (user_id) references User(id)
);

create table SessionGameCopy (
    session_id integer not null,
    game_id integer not null,
    store_id integer not null,
    copy_num integer not null,
    foreign key (session_id) references Session(id),
    foreign key (game_id, store_id, copy_num) references GameCopy(game_id, store_id, copy_num),
    primary key (session_id, game_id, store_id, copy_num)
);

create table GameDamage (
    session_id integer not null,
    game_id integer not null,
    store_id integer not null,
    copy_num integer not null,
    description text,
    foreign key (session_id) references Session(id),
    foreign key (game_id, store_id, copy_num) references GameCopy(game_id, store_id, copy_num),
    primary key (session_id, game_id, store_id, copy_num)
);


-- create table tier (
--     tier_id   integer primary key autoincrement,
--     tier_name text not null
-- );
