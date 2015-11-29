DROP TABLE if EXISTS user;

CREATE TABLE user (
 id_user integer PRIMARY KEY autoincrement,
 name_user varchar(30) NOT NULL,
 password_user varchar(30) NOT NULL,
 email_user varchar(30) NOT NULL
);

DROP TABLE if EXISTS pubs;

CREATE TABLE pubs (
  pubname text,
  pubtype text,
  pubadress text,
  openingtimes text,
  website text
);