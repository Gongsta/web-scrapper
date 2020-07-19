"""Script that scrapes jobs from https://www.jobbank.gc.ca/"""
import bs4 as bs
from selenium import webdriver
import time
import json


province = "QC"
url = "https://www.jobbank.gc.ca/jobsearch/jobsearch?sort=M&fprov=QC"

#For Mac - If you use windows change the chromedriver location
chrome_path = '/usr/local/bin/chromedriver'


def scrapeJob(url):
    # use the session to get the data
    driver = webdriver.Chrome(chrome_path)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-popup-blocking")

    driver.maximize_window()
    driver.get(url)

    start_time = time.monotonic()

    while True:
        try:
            driver.find_element_by_id('moreresultbutton').click()
            time.sleep(0.4)
            print("getting jobs,", 'minutes elapsed: ', (time.monotonic() - start_time) / 60)

        except:
            print("got all jobs")
            break

    soup = bs.BeautifulSoup(driver.page_source, 'html.parser')
    js_test = soup.find_all('article')

    jobIds = []

    for i,element in enumerate(js_test):
        jobId = int(element.get("id")[-8:])
        jobIds.append(jobId)


    print(len(jobIds))


    #Iterating over the current database of jobs, removing all jobs that are already on the database
    with open("/Users/stevengong/Projects/matilda-scrapper/jobs.json", 'r') as f:
        oldJobIds = json.load(f)
        for id in jobIds:
            if id in oldJobIds:
                jobIds.remove(id)
        allJobs = oldJobIds + jobIds

    #Overwriting the newJobs.json with jobs that aren't on the database
    with open("/Users/stevengong/Projects/matilda-scrapper/newJobs.json", 'w') as file:
            # indent=2 is not needed but makes the file
            # human-readable for more complicated data
        json.dump(jobIds, file, indent=2)

        #Appending the current jobs database

    with open("/Users/stevengong/Projects/matilda-scrapper/jobs.json","w") as file:
        json.dump(allJobs, file, indent=2)



if __name__ == '__main__':
    scrapeJob(url)

