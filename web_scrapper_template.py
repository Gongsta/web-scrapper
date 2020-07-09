#A webscrapper using BeautifulSoup

import bs4
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

my_url = "https://www.newegg.ca/Video-Cards-Video-Devices/Category/ID-38?Tpk=graphics%20card"

#Opening the connection from the url
uClient= uReq(my_url)
#reading from the page
page_html = uClient.read()
#Closing the client
uClient.close()
#Second argument is how it is parsed
page_soup = soup(page_html, "html.parser")

#Returns a list of all the elements with class item-container
containers = page_soup.findAll('div', {'class':'item-container'})

filename = "products.csv"
f = open(filename, 'w')
headers = "brand, product_name, shipping\n"
f.write(headers)

#You use the dot(.) notation to access the element 
for container in containers:	
	brand = container.find('div', 'item-info').div.a.img['title']
	name = container.find('a', 'item-title').text
	#The strip function removes extra spaces and /r/n
	shipping = container.find('li', 'price-ship').text.strip()

	print(brand)
	print(name)
	print(shipping)

	#The name has commas so gotta replace it so it doesn't create new columns

	f.write(brand + ',' + name.replace(',','|') + ',' + shipping + '\n')