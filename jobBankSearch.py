"""Script that scrapes jobs from https://www.jobbank.gc.ca/"""
from dynamicScrapper import Page
import bs4 as bs
from jobBankSpecificJob import scrape_job_page
import time

url = "https://www.jobbank.gc.ca/jobsearch/jobsearch?fjsf=1&sort=D"

def main():
    page = Page(url)
    soup = bs.BeautifulSoup(page.html, 'html.parser')
    js_test = soup.find_all('article')

    for i,element in enumerate(js_test):
        jobId = element.get("id")[-8:]
        jobUrl = "https://www.jobbank.gc.ca/jobsearch/jobposting/" + jobId
        scrape_job_page(jobUrl)
        print("job scrapped")


if __name__ == '__main__':
    main()
