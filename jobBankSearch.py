"""Script that scrapes jobs from https://www.jobbank.gc.ca/"""
import bs4 as bs
from selenium import webdriver
import time
import csv

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

    jobTitles = []

    for i,element in enumerate(js_test):
        jobId = element.get("id")[-8:]
        jobUrl = "https://www.jobbank.gc.ca/jobsearch/jobposting/" + jobId
        jobTitles.append(jobUrl)


    print(len(jobTitles))

    for i, job in enumerate(jobTitles):
        print(job)
        with open("index.csv", "a") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([job])

if __name__ == '__main__':
    scrapeJob(url)

