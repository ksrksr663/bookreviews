# This program imports all the data from the 'books.csv' file into a PostgreSQL database

import csv
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

try:
    engine = create_engine(os.getenv("DATABASE_URL"))
except AttributeError:
    print("You did not define the environmental variable 'DATABASE_URL'!")
    print("Program Ended")
    sys.exit(1)  # exit the program with an exit code of 1
except Exception as e:
    print(e, type(e))
    sys.exit(1)
else:  # if there were no exceptions run the below line of code
    db = scoped_session(sessionmaker(bind=engine))

entry = 0  # count the number of books the program imported into the PostgreSQL database

with open("books.csv", 'r') as fin:
    reader = csv.reader(fin)
    first_line = True

    for isbn, title, author, year in reader:
        if first_line is True:
            first_line = False
            continue  # skip the first line only

        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added the book '{title}', written by '{author}'")
        entry += 1

    db.commit()  # close the transaction


print(f"Inserted {entry} books into the PostgreSQL database")
print("Program Ended")


