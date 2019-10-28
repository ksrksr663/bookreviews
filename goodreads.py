"""
This Python program abstracts the functionality of using the Goodreads API when it is being used as a module.
"""


import os
import requests
import set_environ_var  # this module sets up environmental variables

# set up the environmental variable "API_KEY_GOODREADS"
set_environ_var.api_key_goodreads()  

# set up the important constant global variables
# KEY = os.getenv("API_KEY_GOODREADS")  # read its value
KEY = os.environ["API_KEY_GOODREADS"]  # -> you can also code it like this
REQ_URL = "https://www.goodreads.com/book/review_counts.json"
# ISBN = "0553588486"  # the ISBN number for 'A Game of Thrones"


def main(ISBN):
    params = {
        "key": KEY,
        "isbns": ISBN
    }
    res = requests.get(REQ_URL, params=params)
    res = res.json()
    # print(res)

    number_of_rating = res['books'][0]['work_ratings_count']
    average_rating = res['books'][0]['average_rating']
    # print("number of ratings:", number_of_rating, "\naverage rating:", average_rating)

    # TODO: maybe use a named tuple from the collections module instead of a dictionary
    book_info = {
        "number of ratings": number_of_rating,
        "average rating": average_rating
    }
    return book_info


if __name__ == "__main__":
    main(ISBN)

