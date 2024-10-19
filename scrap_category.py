import requests
from bs4 import BeautifulSoup
import csv

category_page_url = "https://books.toscrape.com/catalogue/category/books/sequential-art_5/index.html"
response = requests.get(category_page_url)
page = response.content
soup = BeautifulSoup(page, "html.parser")



