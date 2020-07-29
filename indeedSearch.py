"""Script that scrapes jobs from https://ca.indeed.com/"""
import bs4 as bs
from selenium import webdriver
import time
import requests
import datetime
from datetime import timedelta
import json
from functions import *

province = "QC"
url = "https://ca.indeed.com/jobs-in-QC"

#For Mac - If you use windows change the chromedriver location
chrome_path = '/usr/local/bin/chromedriver'
driver = webdriver.Chrome(chrome_path)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-popup-blocking")

driver.maximize_window()


def scrapeJobListings(url):
    # use the session to get the data
    driver.get(url)

    soup = bs.BeautifulSoup(driver.page_source, 'html.parser')
    jobListings = soup.find_all('div', "jobsearch-SerpJobCard unifiedRow row result clickcard") #Second argument is the class

    jobIds = []

    for i,element in enumerate(jobListings):
        jobId = element.get("data-jk")
        jobIds.append(jobId)

    return jobIds
    #
    #
    # print(len(jobIds))
    #
    #
    # #Iterating over the current database of jobs, removing all jobs that are already on the database
    # with open("/Users/stevengong/Projects/matilda-scrapper/indeedJobs.json", 'r') as f:
    #     oldJobIds = json.load(f)
    #     for id in jobIds:
    #         if id in oldJobIds:
    #             jobIds.remove(id)
    #     allJobs = oldJobIds + jobIds

    # #Overwriting the newJobs.json with jobs that aren't on the database
    # with open("/Users/stevengong/Projects/matilda-scrapper/newIndeedJobs.json", 'w') as file:
    #         # indent=2 is not needed but makes the file
    #         # human-readable for more complicated data
    #     json.dump(jobIds, file, indent=2)
    #
    #     #Appending the current jobs database
    #
    # with open("/Users/stevengong/Projects/matilda-scrapper/indeedJobs.json","w") as file:
    #     json.dump(allJobs, file, indent=2)

jobUrl="https://ca.indeed.com/jobs?l=QC&start&vjk=3e1ca64286e89d9a"
def scrapeJob(jobUrl,id):
    driver.get(jobUrl)

    soup = bs.BeautifulSoup(driver.page_source, 'html.parser')
    container = soup.find('div', id="vjs-container")  # Second argument is the class

    title = container.find(id="vjs-jobtitle").text
    try:
        company = soup.find("div", {"data-jk": id}).find('span', 'company').text.strip()
    except:
        company = None

    try:
        baseSalary = soup.find("div", {"data-jk": id}).find('span', 'salaryText').text.strip()
        if "hour" in baseSalary:
            salaryType = "hourly"
            if "-" in baseSalary:
                #Take the average of the range
                baseSalary = (float(baseSalary[1:6])+float(baseSalary[10:15]))/2
            else:
                baseSalary = float(baseSalary[1:6])

        # elif "week" in baseSalary:
        #     salaryType = "weekly"
        #     if "-" in baseSalary:
        #         baseSalary = (float(baseSalary[1:4])+float(baseSalary[9:12]))/2
        #     else:
        #         baseSalary = float(baseSalary[1:4])
        #
        # elif "month" in baseSalary:
        #     salaryType = "monthly"
        #     if "to" in baseSalary:
        #         baseSalary = (float(baseSalary[1:4])+float(baseSalary[9:12]))/2
        #     else:
        #         baseSalary = float(baseSalary[1:4])

        elif "year" or "annually" in baseSalary:
            salaryType = "yearly"
            if "-" in baseSalary:
                #Take the average of the range
                if len(baseSalary) == 24: #ex: '$38,400 - $40,000 a year'
                    baseSalary = (float(baseSalary[1:7].replace(",",""))+float(baseSalary[11:18].replace(",","")))/2

                elif len(baseSalary) == 25: #ex: '$88,400 to $140,000 annually'
                    baseSalary = (float(baseSalary[1:7].replace(",",""))+float(baseSalary[11:19].replace(",","")))/2

                elif len(baseSalary) == 26: #ex: '$138,400 to $140,000 annually'
                    baseSalary = (float(baseSalary[1:8].replace(",",""))+float(baseSalary[12:20].replace(",","")))/2

            else:
                baseSalary = float(baseSalary[1:7].replace(",",""))
    except:
        baseSalary = None

    if not baseSalary:
        salaryType = None

    workHours = None
    employmentType = None
    location = container.find(id="vjs-loc").text.strip()
    description = container.find(id="vjs-desc").text.strip()

    try:
        days = timedelta(int(container.find("span", "date").text.strip()[:2]))
        datePosted = datetime.datetime.now() - days


    except:
        datePosted = None

    advertisedUntil = None


    try: #External job site if it works
        url = requests.get("https://ca.indeed.com"+ container.find("a", {"class": "view-apply-button blue-button"})["href"]).url[:-14]
    except:
        url = jobUrl

    logo = findCompanyLogo(company)

    job = Job(title, company, salaryType, baseSalary, workHours, employmentType, location, datePosted, advertisedUntil, url, logo)

    job.description = description

    uploadToFirebase(job, id)
    print("job uploaded:", title)
    time.sleep(2)







if __name__ == '__main__':
    for i in range(13290, 100000, 10):
        #QC 12930
        #ON 10280
        url = "https://ca.indeed.com/jobs?l=ON&start=" + str(i)
        jobIds = scrapeJobListings(url)

        for jobId in jobIds:
            jobUrl = url + "&vjk=" + jobId

            try:
                scrapeJob(jobUrl, jobId)
            except:
                print("job is corrupt")
        start_time = time.monotonic()
        time.sleep(10)
        print("getting jobs,", 'minutes elapsed: ', (time.monotonic() - start_time) / 60)

