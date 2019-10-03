import pandas as pd
import numpy as np
import requests as req
import pprint as pp
import json
import csv
import os
import sys

# as an example, "https://openlibrary.org/api/books?bibkeys=ISBN:0451526538&format=json&jscmd=data"

# the documentation of the API can be found here: https://openlibrary.org/dev/docs/api/books

def book_check(book_number):

    # signal flags for [ISBN, author, publisher, subject, title ]
    # in case they are missing in the data base. 
    flags = [0,0,0,0,0]

    author = None
    publisher = None
    title = None

    # specify the url
    url_pt1 = "https://openlibrary.org/api/books?bibkeys=ISBN:"
    ISBN = book_number 
    url_pt2 = "&format=json&jscmd=data"
    url = url_pt1 + ISBN + url_pt2

    # get the response
    response = req.get(url)

    # parse the json data
    byte_json = response.content
    data_json = byte_json.decode('utf8')# .replace("'", '"')
    parsed_data = json.loads(data_json)
    master_key = "ISBN:" + ISBN
    # handle the case where ISBN is wrong or not available
    try:
        parsed_data2 = parsed_data[master_key]
    except:
        print("There is no book with this ISBN. Input ISBN again.")
        return 

    # get the information we need
    try:
        author = parsed_data2["authors"][0]["name"]
    except KeyError as error:
        flags[1] = 1
        print("author info is not available.")

    try:
        publisher = parsed_data2['publishers'][0]["name"]
    except KeyError as error:
        print("Publisher info is not available.")
        flags[2] = 1

  
    try:
        title = parsed_data2['title']
    except KeyError as error:
        print("title info is not available.")
        flags[4] = 1 

    # if any of the flags is triggered
    if(flags != [0,0,0,0,0]):
        key = input("Some of the info are missing. Do you still want to log the book? Y/N \n")
        if key == "Y":
            print("Book is logged.")

        if key == "N":
            print("Logging forfeited.")
            return



    row = [ISBN, author, publisher, title]
    print(row)
    

    # check if the file has been created, if not, create one
    exists = os.path.isfile("./book_log.csv")
    if exists: 
        with open("book_log.csv", "a", newline='') as csvFile:
            filewriter = csv.writer(csvFile)
            filewriter.writerow(row)
        csvFile.close()

    else: 
        with open("book_log.csv", "w", newline='') as csvFile:
            filewriter = csv.writer(csvFile, delimiter=",")
            filewriter.writerow(["ISBN", "Author", "Publisher", 
                                "Title"])
            filewriter.writerow(row)
        csvFile.close()

    return 

    # return({"author":author, "publisher":publisher, "title":title, "ISBN":ISBN})

    
def main():
    while(True):
        num = input("Enter the ISBN. If finished, type \'quit\': \n")
        if num == "quit":
            break
        book_check(num)


if __name__ == "__main__":
    main()

