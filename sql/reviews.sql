CREATE TABLE reviews (
	id SERIAL PRIMARY KEY,
	users VARCHAR REFERENCES users,
	isbn VARCHAR REFERENCES books,
	reviews VARCHAR NOT NULL
);

ALTER TABLE reviews ADD COLUMN rating INTEGER CHECK (rating > 0 AND rating < 6);

