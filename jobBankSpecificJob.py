from requests_html import HTMLSession
import bs4 as bs
from google.cloud import firestore
import os
from jobObject import Job
from datetime import datetime
import json


# Initializing a Cloud firestore session with service account keys
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./service-account.json"
db = firestore.Client()

#Initializing a session for web scraping
session = HTMLSession()


def scrape_job_page(id):
    url = "https://www.jobbank.gc.ca/jobsearch/jobposting/" + str(id)
    # use the session to get the data
    r = session.get(url)
    print("got session")
    # Render the page, up the number on scrolldown to page down multiple times on a page
    r.html.render()
    print("html rendered")
    soup = bs.BeautifulSoup(r.content, 'html.parser')


    #Standard, formatted data
    title = soup.find("span", property="title").text.strip()
    company = soup.find("span", property="hiringOrganization").text.strip()
    employmentType = soup.find("span", property="employmentType").get_text(separator=", ").strip()
    location = soup.find("span", property="jobLocation").text.strip().replace("\n"," ").replace("\t","")
    #Converting string date to datetime date
    datePosted = datetime.strptime(soup.find("span", property="datePosted").text.strip()[10:], "%B %d, %Y")

    try:
        advertisedUntil = datetime.strptime(soup.find(property="validThrough").text.strip(), "%Y-%m-%d") #<p> tag
    except:
        advertisedUntil = None

    try:
        baseSalary = soup.find("span", property="baseSalary").text.strip().replace("HOUR","").replace("$$","$").replace("YEAR","").replace("WEEKLY","")
    except:
        baseSalary = None

    try:
        workHours = soup.find("span", property="workHours").text.strip()
    except:
        workHours = None

    #Difficult to format. Not important things like vacancies, verified or not, jobId
    # cardDescription = soup.find("ul", {"class": "job-posting-brief"}) #<ul>
    # cardKeys = []
    # cardValues = []
    # for div in cardDescription.find_all("span", {"class": "wb-inv"}):
    #     cardKeys.append(div.text)
    #     div.decompose()
    #
    # for element in cardDescription.find_all("li"):
    #     cardValues.append(element.text.replace("\t",'').replace("\n","").lstrip())
    #
    # cardKeys.remove("$")

    #External and internal jobs on JobBank have different formatting, this is the procedure
    try:
        jobUrl = soup.find(id="externalJobLink").get("href")
        containsDescription = False
        containsEmploymentGroup = False
        containsSpecialCommitments = False


    except: #if there is an error, it means there is no externalLink, i.e. the jobApplication is hosted on jobBank itself. More information to scrape
        print("No external link, hosted on JobBank")
        containsDescription = True

        jobUrl = url
        language = soup.find("div", {"class": "job-posting-detail-requirements"}).p.text
        educationRequirements = soup.find(property="educationRequirements").text  # <p>
        experienceRequirements = soup.find(property="description experienceRequirements").text  # <p>

        try:
            employmentGroup = soup.find(id="employmentGroup").p.text  # <div>
            containsEmploymentGroup = True
        except:
            containsEmploymentGroup = False

        try:
            specialCommitments = soup.find("span", property="specialCommitments").text.strip()
            containsSpecialCommitments = True
        except:
            containsSpecialCommitments = False

        #A.k.a advanced description
        skills = soup.find(property="skills")  # <div>

        try:
            skills.text
            skillKeys = []
            skillValues = []
            for element in skills.find_all("dt"):
                skillKeys.append(element.text)
            for element in skills.find_all("dd"):
                skillValues.append(element.text)

            description = {}
            for index, key in enumerate(skillKeys):
                description[key] = skillValues[index]
            #howtoapply = soup.find(id="howtoapply")  #TODO <div>. This doesn't work because we have to click on a button.
        except:
            description = None

    #Uploading to firebase
    job = Job(title, company, baseSalary, workHours, employmentType, location, datePosted, advertisedUntil, jobUrl)
    print("Job initialized")
    if containsDescription:
        job.description = description
        job.language = language
        job.educationRequirements = educationRequirements
        job.experienceRequirements = experienceRequirements

    if containsEmploymentGroup:
        job.employmentGroup = employmentGroup

    if containsSpecialCommitments:
        job.specialCommitments = specialCommitments

    print("trying to upload to FB")
    uploadToFirebase(job)
    print("job uploaded:", title)



def uploadToFirebase(job):
    data = {'title': job.title,
            'company': job.company,
            "baseSalary": job.baseSalary,
            "workHours": job.workHours,
            "location": job.location,
            "specialCommitments": job.specialCommitments,
            "datePosted": job.datePosted,
            "advertisedUntil": job.advertisedUntil,
            "url": job.url,
            'description': job.description,
            "language": job.language,
            "educationRequirements": job.educationRequirements,
            "experienceRequirements": job.experienceRequirements,
            "employmentGroup": job.employmentGroup
            }
    # db.collection("jobs").add(data)

    #Uploading to firebase

#For testing purposes
# https://www.jobbank.gc.ca/jobsearch/jobposting/32606863
# scrape_job_page("https://www.jobbank.gc.ca/jobsearch/jobposting/32646181")
# scrape_job_page("https://www.jobbank.gc.ca/jobsearch/jobposting/32606884")
# create the session

if __name__ == "__main__":
    with open("newJobs.json", 'r') as f:
        jobIds = json.load(f)

    for jobId in jobIds:
        print(jobId)
        # scrape_job_page(job)

    # with open("index.csv") as csvfile:
    #     readCSV = csv.reader(csvfile, delimiter=",")
    #     count = 0
    #     for row in readCSV:
    #         count += 1
    #         print(count)
    #
    #         try:
    #             scrape_job_page(row[0])
    #         except Exception as e:
    #             print(e)

