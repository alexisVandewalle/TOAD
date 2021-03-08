-- TODO remove this comments
-- TODO create a table with ui connected to a user
-- DROP TABLE IF EXISTS user;
-- DROP TABLE IF EXISTS eth_public_key;
DROP TABLE IF EXISTS gsk;
DROP TABLE IF EXISTS gpk;
DROP TABLE IF EXISTS share;
DROP TABLE IF EXISTS encrypted_file;
DROP TABLE IF EXISTS mpk;
/*
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  private_key TEXT UNIQUE NOT NULL,
  account_address TEXT UNIQUE NOT NULL
);

CREATE TABLE eth_public_key (
  account_address TEXT UNIQUE NOT NULL,
  pk_x TEXT UNIQUE NOT NULL,
  pk_y TEXT UNIQUE NOT NULL
);*/

CREATE TABLE gpk (
    x TEXT,
    y TEXT,
    ui TEXT,
    round INT
);

CREATE TABLE encrypted_file (
    round INTEGER,
    hash TEXT,
    c1x TEXT,
    c1y TEXT,
    c2x TEXT,
    c2y TEXT,
    sender TEXT NOT NULL
);

CREATE TABLE share (
    round INTEGER,
    a TEXT,
    b TEXT,
    ui TEXT
);

CREATE TABLE gsk (
    gsk TEXT,
    ui TEXT,
    round INT
);

CREATE TABLE mpk (
    x TEXT,
    y TEXT,
);
