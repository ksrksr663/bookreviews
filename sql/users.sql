CREATE TABLE users (
	number SERIAL,
	first_name VARCHAR NOT NULL,
	last_name VARCHAR NOT NULL,
	username VARCHAR PRIMARY KEY,
	password VARCHAR NOT NULL 
);

