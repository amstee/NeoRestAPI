CREATE TABLE    user(
  id            INTEGER PRIMARY KEY, 
  email         VARCHAR(255),
  password      VARCHAR(64),
  fname         VARCHAR(255),
  lname         VARCHAR(255),
  birthday      VARCHAR(255),
  webtoken      VARCHAR(64),
  devicetoken   VARCHAR(64) 
);
CREATE TABLE    device(
  id            INTEGER PRIMARY KEY,
  userid        INTEGER,
  mid           VARCHER(255),
  FOREIGN KEY(userid) REFERENCES user(id)  
);