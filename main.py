import requests
from bs4 import BeautifulSoup
import re
import os
import urllib.parse
import csv

#Get soup from url
def get_soup(url):
    response = requests.get(url)
    page = response.content
    soup = BeautifulSoup(page, "html.parser")

    return soup

#Get all categories URLs
def get_categories():
    soup = get_soup("https://books.toscrape.com/index.html")
    list = soup.select("ul.nav-list li ul li a")
    categories = []
    for href in list:
        url = f"https://books.toscrape.com/{href["href"].replace("index.html", "")}"
        categories.append(url)
    
    return categories

#Get all pages per category
def get_pages(category_url):
    category_pages = []
    page = 1
    while True : 
        url = f"{category_url}page-{str(page)}.html"
        if 'page-1.html' in url :
            url = url.replace('page-1.html', 'index.html') 
        response = requests.get(url)
        if response.status_code == 200:
            category_pages.append(url)
            page += 1
        else:
            page = 1
            break
    
    return category_pages

#Get all books from a page
def get_books(page_url):
    soup = get_soup(page_url)
    list = (soup.select("h3 > a"))
    books = []
    for book in list:
        books.append(f"https://books.toscrape.com/catalogue/{(book["href"]).strip("../")}")

    return books

#Get book data
def get_book_data(book_url):
    url = book_url
    soup = get_soup(book_url)
    response = requests.get(url)
    book_data = []

    if response.ok :
        breadcrumb = soup.find('ul', {'class': 'breadcrumb'})

        page_url = response.url

        #Book category
        category = breadcrumb.find_all('a')[2].string

        #Book Title
        title = breadcrumb.find("li", class_="active").string
        title = re.sub("[^a-zA-Z0-9 \n \'.']", '', title)

        #Book Image URL
        image_url = f"https://books.toscrape.com/{(soup.find("img"))["src"].strip("../..")}"

        #Download Image
        response = requests.get(image_url)
        directory = "book_images"
        if not os.path.exists(directory):
            os.makedirs(directory)
        category_directory = os.path.join(directory, category)
        if not os.path.exists(category_directory):
            os.makedirs(category_directory)
        file_name = title + ".jpg"
        encoded_file_name = urllib.parse.urlencode({'name': file_name})[5:]
        with open(os.path.join(category_directory, encoded_file_name), "wb") as f:
            f.write(response.content)

        #Book Rating
        rating_num = (soup.find("p", class_="star-rating")).attrs["class"]
        str_to_num = {
            'Zero': '0',
            'One': '1',
            'Two': '2',
            'Three': '3',
            'Four': '4',
            'Five': '5'
        }
        rating = f"{str_to_num[rating_num[1]]} out of 5"

        #Book Description
        description = soup.find("p", class_= None)
        if description == None:
            description = "No description"
        else:
            description = description.string
        description = re.sub("[^a-zA-Z0-9 \n \'.' \'()']", '', description)

        #Book UPC
        upc = soup.find_all("td")[0].string

        #Book Prices
        price_excluding_tax = soup.find_all("td")[2].string
        price_including_tax = soup.find_all("td")[3].string

        #Book Availability
        availability = (soup.find_all("td")[5].string).strip("In stock ()")

        #Put all data in list
        book_data.append(page_url)
        book_data.append(upc)
        book_data.append(title)
        book_data.append(price_including_tax)
        book_data.append(price_excluding_tax)
        book_data.append(availability)
        book_data.append(description)
        book_data.append(category)
        book_data.append(rating)
        book_data.append(image_url)

        return category, book_data

#CSV generation
def create_csv_file(category_name, book_data):
    csv_directory = "CSV_files"
    if not os.path.exists(csv_directory):
        os.makedirs(csv_directory)
    with open(os.path.join(csv_directory, f"{category_name}.csv"), "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        csv_header = ["Product URL", "UPC", "Title", "Price incl. taxes", "Price excl. taxes", "Availability", "Description", "Category", "Rating", "Image URL"]
        writer.writerow(csv_header)
        writer.writerows(book_data)

#Combining function to scrap all product on BooksToScrap
def scrap_all():
    categories = get_categories()
    for category in categories:
        pages = get_pages(category)
        book_data = []
        for page in pages:
            books = get_books(page)
            for book_url in books:
                book_info = get_book_data(book_url)
                category = book_info[0]
                book_data.append(book_info[1])           
        create_csv_file(category, book_data)
scrap_all()