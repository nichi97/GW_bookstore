from googleapiclient.discovery import build
import os

import pandas as pd


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
    author_names = raw_name.split(" ", maxsplit=1)
    if len(author_names) > 1:
        return author_names[1] + ", " + author_names[0]
    else:
        return raw_name


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


def web_log(ISBN, data, vol):
    author = ""
    publisher = ""
    title = ""
    found13 = True

    output = vol.list(q="isbn:" + ISBN, maxResults=1).execute()
    if len(output["items"]) == 0:
        print("No book found with this ISBN.")
        return
    info = output["items"][0]["volumeInfo"]

    # handle the case where the input is ISBN 10, not 13. We convert it to
    # ISBN 13 if possible. Else, send warning.
    if ISBN[:3] != "978":
        found13 = False
        for identifier in info["industryIdentifiers"]:
            if identifier["type"] == "ISBN_13":
                found13 = True
                ISBN = identifier["identifier"]
        if not found13:
            print("The ISBN number you typed in is ISBN 10, not ISBN13. There is no ISBN13 number in database for "
                  "this book.")

    # get the information we need
    if "authors" in info and len(info["authors"]) > 0:
        author = info["authors"][0]
    else:
        print("author info is not available.")

    if "publisher" in info:
        publisher = info['publisher']
    else:
        print("Publisher info is not available.")

    if "title" in info:
        title = info['title']
    else:
        print("title info is not available.")

    if "subtitle" in info:
        # if the book has a subtitle, use the subtitle as well.
        subtitle = info['subtitle']
        title = title + ": " + subtitle

    # if any info is missing
    if not author or not title or not publisher or not found13:
        key = input("Some of the info are missing. Do you still want to log the book? Y/N \n").upper().strip()
        if key == "Y":
            print("Book is logged.")
        if key == "N":
            print("Logging forfeited.")
            return

    author = reformat_name(author)
    quantity, in_log, data = merge_book(ISBN, data)
    if not in_log:
        price = input("Enter the price of this book: ")
        data = data.append({'ISBN': int(ISBN), 'Author': author,
                            'Title': title, 'Publisher': publisher, 'Quantity': 1, 'Price': float(price)},
                           ignore_index=True)

    data.to_excel("book_log.xlsx", index=False)
    row = [ISBN, author, publisher, title, quantity]
    print(row)

    return data


def main():
    with open("key.txt", "r") as f:
        api_key = f.readline().strip()
    service = build("books", "v1", developerKey=api_key)
    vol = service.volumes()
    while True:
        data = update_books()
        num = input("Enter the ISBN. If finished, type \'quit\': \n").strip()
        if num == "quit":
            break
        data = web_log(num, data, vol)


if __name__ == "__main__":
    main()

# with open("key.txt", "r") as f:
#     api_key = f.readline().strip()
# service = build("books", "v1", developerKey=api_key)
# vol = service.volumes()
# # print(vol)
# output = vol.list(q="isbn:9781583671535", maxResults=1).execute()
# print(output["items"][0])
