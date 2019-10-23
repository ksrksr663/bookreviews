import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

with open("books.csv", 'r') as fin:
    reader = csv.reader(fin)
    first_line = True
    i = 0

    for isbn, title, author, year in reader:
        if first_line is True:
            first_line = False
            continue  # skip only the first line

        print(f"The ISBN is: {isbn}, the author is {author}, the title is {title}, the year it was published is {year}")
        i = i + 1  
        if i >= 10:  # print only the first ten lines
            break


print("Program Ended")


