from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import csv
from datetime import datetime

city = "montreal"
query = "Software Developer Jobs".replace(" ", "-")

#Query with spaces don't work, so you will have to replace with a dash
url = "https://indeed.com/" + query
url.replace(" ", "-")

uClient= urlopen(url)
#reading from the page
page_xml = uClient.read()
#Closing the client
uClient.close()
#Second argument is how it is parsed
page_soup = soup(page_xml)

#I need to go by links since the email informations are there
jobLinks = page_soup.findAll('rdf:li')
links = []
# jobListings = page_soup.findAll('item')
# descriptions = page_soup.findAll('description')

#Do a query
for job in jobLinks:
    links.append(job.get('rdf:resource'))
    # job.find('title').text.strip()
    # job.find("description").text.strip()
    # job.find('link').text.strip()

#Going into the respective pages to obtain more detailed information

jobDescriptions = []
jobTitles = []
jobAttributes = []

for link in links:
    uClient = uReq(link)
    # reading from the page
    page = uClient.read()
    # Closing the client
    uClient.close()
    page = soup(page)

    wantedDescription = page.find("section", {"id": "postingbody"})
    #Removing the find QR code text
    unwantedDescription = wantedDescription.find('p', {'class': 'print-qrcode-label'}).extract()

    #Appending to an array
    jobDescriptions.append(wantedDescription.text.strip().title())
    jobTitles.append(page.find(True, {"class": "postingtitle"}).text.strip())
    jobAttributes.append(page.find("p", {"class": "attrgroup"}).text.strip())


# open a csv file with append ("a"), so old data will not be erased

for i in range(len(jobTitles)):
    with open("index.csv", "a") as csv_file:
     writer = csv.writer(csv_file)
     writer.writerow([jobTitles[i], jobDescriptions[i], jobAttributes[i], datetime.now()])
