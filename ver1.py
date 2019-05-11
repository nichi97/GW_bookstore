import pandas as pd
import numpy as np
import requests as req
import pprint as pp
import json
import sys

# as an example, "https://openlibrary.org/api/books?bibkeys=ISBN:0451526538&format=json&jscmd=data"

# the documentation of the API can be found here: https://openlibrary.org/dev/docs/api/books

def book_check(book_number):
    # specify the url
    url_pt1 = "https://openlibrary.org/api/books?bibkeys=ISBN:"
    ISBN = book_number 
    url_pt2 = "&format=json&jscmd=data"
    url = url_pt1 + ISBN + url_pt2

    # get the response
    response = req.get(url)

    # parse the json data
    byte_json = response.content
    data_json = byte_json.decode('utf8').replace("'", '"')
    parsed_data = json.loads(data_json)
    master_key = "ISBN:" + ISBN
    # handle the case where ISBN is wrong or not available
    try:
        parsed_data2 = parsed_data[master_key]
    except:
        print("There is no book with this ISBN. Input ISBN again.")
        return 

    # get the information we need
    author = parsed_data2["authors"][0]["name"]
    publisher = parsed_data2['publishers'][0]["name"]
    subjects = parsed_data2['subjects'][0]["name"]
    title = parsed_data2['title']

    return({"author":author, "publisher":publisher, "subjects":subjects, "title":title, "ISBN":ISBN})

    
def main():
    while(True):
        num = input("Enter the ISBN: ")
        print(book_check(num))


if __name__ == "__main__":
    main()

