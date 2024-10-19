import requests
from bs4 import BeautifulSoup
import csv

product_page_url = "https://books.toscrape.com/catalogue/scott-pilgrims-precious-little-life-scott-pilgrim-1_987/index.html"
response = requests.get(product_page_url)
page = response.content
soup = BeautifulSoup(page, "html.parser")

title = soup.find("h1").string
category_link = soup.find_all("a")[3]
category = category_link.string
image = soup.find("img")
image_url = f"https://books.toscrape.com{image.attrs["src"]}"
rating = soup.find("p", class_="star-rating")
review_rating = rating.attrs["class"][1]
description_title = soup.find_all("p")[3]
product_description = description_title.string
product_infos = soup.find_all("td")
universal_product_code = product_infos[0].string
price_excluding_tax = product_infos[2].string
price_including_tax = product_infos[3].string
number_available = product_infos[5].string

heading = ["title", "product_page_url", "category", "image_url", "review_rating", "product_description", "universal_product_code", "price_excluding_tax", "price_including_tax", "number_available"]
with open("data.csv", "w") as csv_file:
    writer = csv.writer(csv_file, delimiter=",")
    writer.writerow(heading)
    line = [title, product_page_url, category, image_url, review_rating, product_description, universal_product_code, price_excluding_tax, price_including_tax, number_available]
    writer.writerow(line)