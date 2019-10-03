import pandas as pd
import numpy as np
import requests as req
import pprint as pp
import json
import csv
import os
import sys

# This version is aiming for: 
# 1. Add quanlity column in the spread sheet
# 2. Add a rudimentary sell mode in which scanned book's quantity will reduce  
#    by 1
# 3. 

# as an example, "https://openlibrary.org/api/books?bibkeys=ISBN:0451526538&format=json&jscmd=data"

# the documentation of the API can be found here: https://openlibrary.org/dev/docs/api/books

def update_books():

    """
    This function read the file book_log.csv in the directory

    Input: None
    Output: None
    Side effect: create or change data
    """

    global ISBN_quantity_dict 
    global is_defined 

    exists = os.path.isfile("./book_log.csv")

    if exists:
        
        is_defined = True
        data = pd.read_csv("./book_log.csv")
        ISBN_quantity_dict = dict(zip(data["ISBN"], data["Quantity"]))


    else:

        is_defined = False
        #data = pd.DataFrame(np.array(["ISBN", "Author", "Publisher", 
        #                        "Title", "Quantity"])).T
        data = pd.DataFrame(columns=["ISBN", "Author", "Publisher", 
                                "Title", "Quantity"])

        #with open("book_log.csv", "w", newline='') as csvFile:
        #    filewriter = csv.writer(csvFile, delimiter=",")
        #    filewriter.writerow(["ISBN", "Author", "Publisher", 
        #                        "Title", "Quantity"])
        #csvFile.close()

    return data



def merge_book(ISBN, data):

    """
    This function check given 
    
    Side effect: Quanlity column of book_log.csv will be updated

    Input: ISBN -- the ISBN number of the new logged book
    Output: in_log -- whether this book is in the book_log or not
    """

    in_log = False 
    updated_book_list = []
    quantity = 1

    # check if book is in book_log.csv
    ISBN = int(ISBN)
    if is_defined and (ISBN in ISBN_quantity_dict):
        # TODO DEBUG
        ISBN_quantity_dict[ISBN] += 1
        updated_book_list.append(ISBN)
        in_log = True  # TODO update prompt

        data.loc[data["ISBN"] == ISBN, "Quantity"] += 1

        quantity = data.loc[data["ISBN"] == ISBN, "Quantity"]

    return quantity, in_log, data 


# def local_log(book_number):


def web_log(book_number, data):

    # signal flags for [ISBN, author, publisher, title ]
    # in case they are missing in the data base. 
    flags = [0,0,0,0]

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
    if(flags != [0,0,0,0]):
        key = input("Some of the info are missing. Do you still want to log the book? Y/N \n")
        if key == "Y":
            print("Book is logged.")

        if key == "N":
            print("Logging forfeited.")
            return

    quantity, in_log, data = merge_book(ISBN,data)
    row = [ISBN, author, publisher, title, quantity]
    if not in_log:
        data = data.append({'ISBN':ISBN, 'Author':author,
            'Title':title, 'Publisher':publisher, 'Quantity':1},
            ignore_index=True)

    data.to_csv("book_log.csv", index = False)
    print(row)
    

    # check if the file has been created, if not, create one

    return data



    
def main():
    while(True):
        data = update_books()
        num = input("Enter the ISBN. If finished, type \'quit\': \n")
        if num == "quit":
            break
        data = web_log(num,data)

    

if __name__ == "__main__":
    main()

