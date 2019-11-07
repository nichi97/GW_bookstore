import pandas as pd
import numpy as np
import requests as req
import pprint as pp
import json
import os
import sys

# This version is aiming for: 
# 1. Add quanlity column in the spread sheet
# 2. Add a rudimentary sell mode in which scanned book's quantity will reduce  
#    by 1
# 3. 

# as an example, "https://openlibrary.org/api/books?bibkeys=ISBN:0451526538&format=json&jscmd=data"

# the documentation of the API can be found here: https://openlibrary.org/dev/docs/api/books


def reformat_name(raw_name):
    """
    This function reformats the name from "first (middle) last" to "last, first"
    input: name from ISBN database
    output: name in "Last, first (middle)" format
    """
    name_ls = raw_name.split()
    # if the raw_name format is "first Last"
    if(len(name_ls) == 2):
        name_formatted = name_ls[1] + ', ' + name_ls[0]
    elif(len(name_ls) == 3):
        name_formatted = name_ls[2] + ', ' + name_ls[0]
    return name_formatted


def update_books():

    """
    This function read the file book_log.xlsx in the directory

    Input: None
    Output: None
    Side effect: create or change data
    """

    global ISBN_quantity_dict 
    global is_defined 

    exists = os.path.isfile("./book_log.xlsx")

    if exists:
        
        is_defined = True
        data = pd.read_excel("./book_log.xlsx")
        ISBN_quantity_dict = dict(zip(data["ISBN"], data["Quantity"]))


    else:

        is_defined = False
        data = pd.DataFrame(columns=["ISBN", "Author", "Publisher", 
                                "Title", "Quantity", "Price"])


    return data




def merge_book(ISBN, data):

    """
    This function check given 
    
    Side effect: Quanlity column of book_log.xlsx will be updated

    Input: ISBN -- the ISBN number of the new logged book
    Output: in_log -- whether this book is in the book_log or not
    """

    in_log = False 
    updated_book_list = []
    quantity = 1

    # check if book is in book_log.xlsx
    ISBN = int(ISBN)
    if is_defined and (ISBN in ISBN_quantity_dict):
        ISBN_quantity_dict[ISBN] += 1
        updated_book_list.append(ISBN)
        in_log = True  

        data.loc[data["ISBN"] == ISBN, "Quantity"] += 1

        quantity = data.loc[data["ISBN"] == ISBN, "Quantity"]

    return quantity, in_log, data 

def update_price(data, ISBN, price):
    """
    This function update the price of a given book
    Input: data -- our database
           ISBN: the ISBN number of the book whose price will be changed to
           price: the new price that we want to change to 
    Output: data 
    Side effect: change the price of a given book in data.
    """
    data.loc[data["ISBN"] == ISBN, "Price"] = price
    return data


def web_log(book_number, data):

    # signal flags for [ISBN, author, publisher, title]
    # in case they are missing in the data base. 
    flags = [0,0,0,0]
    has_subtitle = False

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

    # handle the case where the input is ISBN 10, not 13. We convert it to 
    # ISBN 13 if possible. Else, send warning.
    ISBN_str = str(ISBN)[:3]
    if ISBN_str != str(978):
        try:
            ISBN = parsed_data2["identifiers"]["isbn_13"][0]
            print("ISBN10 automatically converted to ISBN13.")
        except KeyError as error:
            print("The ISBN number you typed in is ISBN 10, not ISBN13. There is no ISBN13 number in database for this book.")
            flags[0] = 1

    

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
        flags[3] = 1 

    try:
        # if the book has a subtitle, use the subtitle as well.
        subtitle = parsed_data2['subtitle']
        has_subtitle = True
    except KeyError as error:
        print("This book does not have any subtitle.")
        

    
    # if the book has a subtitle, update the title to the form "title: subtitle"
    if has_subtitle:
        title = title + ": " + subtitle

    # if any of the flags is triggered
    if(flags != [0,0,0,0]):
        key = input("Some of the info are missing. Do you still want to log the book? Y/N \n")
        if key == "Y":
            print("Book is logged.")

        if key == "N":
            print("Logging forfeited.")
            return

    quantity, in_log, data = merge_book(ISBN,data)
    if not in_log:
        price = input("Please enter the price of this book. \n")
        ISBN_t = str(ISBN) + '\t'
        author = reformat_name(author)
        data = data.append({'ISBN':ISBN_t, 'Author':author,
            'Title':title, 'Publisher':publisher, 'Quantity':1, 'Price':float(price)},
            ignore_index=True)

    data.to_excel("book_log.xlsx", index = False)

    #PRICE_COLUMN = 7
    #price = data.at[data["ISBN"] == int(ISBN), PRICE_COLUMN]
    author = reformat_name(author)
    row = [ISBN, author, publisher, title, quantity]
    print(row)
    
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

