from dynamicScrapper import Page
import bs4 as bs

url = "https://www.jobbank.gc.ca/jobsearch/jobposting/32602551"
url = "https://www.jobbank.gc.ca/jobsearch/jobposting/32564518?source=searchresults"

def scrape_job_page(url):
    page = Page(url)
    soup = bs.BeautifulSoup(page.html, 'html.parser')


    cardDescription = soup.find("ul", {"class": "job-posting-brief"}) #<ul>
    array = []
    for element in cardDescription.find_all("li"):
        array.append(element.text.replace('\n','').replace("\t",''))
        print(element.text.strip())


    advertisedUntil = soup.find(property="validThrough").text.strip() #<p> tag

    try:
        externalLink = soup.find(id="externalJobLink").get("href")
    except:
        print("No external link, hosted on JobBank")
        language = soup.find("div", {"class": "job-posting-detail-requirements"}).p.text
        educationRequirements = soup.find(property="educationRequirements").text  # <p>
        experienceRequirements = soup.find(property="description experienceRequirements").text  # <p>
        skills = soup.find(property="skills")  # <div> # TODO Format this
        employmentGroup = soup.find(id="employmentGroup").p.text  # <div>
        howtoapply = soup.find(id="howtoapply")  # <div>
    # languages =
    # education =
    # experience =
    # specific_skills =
    # transportation =
    # work_conditions =
    # employment_groups =


scrape_job_page("https://www.jobbank.gc.ca/jobsearch/jobposting/32602551")

