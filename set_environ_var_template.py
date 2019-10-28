"""
This Python program sets the important environment variables that is needed for this web application
Remember to add this file to .gitignore!
NOTE: this does not seem to be permanent; TODO: find out why
My solution to this impermanence was to import this file to my main application.py file and call this main function from there.
This is the template file.
"""

import os

def main():
    # to access the PostgreSQL database online
    database_url()
    # the API key for Goodreads
    api_key_goodreads()
    print("Program finished setting up the environment variables.")


def database_url():
    """Sets the 'DATABASE_URL' environment variable"""
    os.environ["DATABASE_URL"] = "some url"


def api_key_goodreads():
    """Sets the 'API_KEY_GOODREADS' environment variable"""
    os.environ["API_KEY_GOODREADS"] = "some key"


if __name__ == "__main__":
    main()

