from requests_html import AsyncHTMLSession
import bs4 as bs
from google.cloud import firestore
import os
from jobObject import Job
from datetime import datetime
import json
import clearbit


# Initializing a Cloud firestore session with service account keys
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/stevengong/Projects/matilda-scrapper/service-account.json"
db = firestore.Client()

#Key for clearbit
clearbit.key = "sk_b090d8a5dbb79e5c1a5d055635543d2b"

#Initializing a session for web scraping
session = AsyncHTMLSession()


async def scrape_job_page():
    # use the session to get the data
    r = await session.get(url)
    # Render the page, up the number on scrolldown to page down multiple times on a page
    await r.html.arender()
    soup = bs.BeautifulSoup(r.content, 'html.parser')


    #Standard, formatted data
    try:
        title = soup.find("span", property="title").text.strip()
    except: #If there is an error, it means the job has expired
        return
    company = soup.find("span", property="hiringOrganization").text.strip()
    try:
        employmentType = soup.find("span", property="employmentType").get_text(separator=", ").strip()
    except:
        employmentType = None
    location = soup.find("span", property="jobLocation").text.strip().replace("\n"," ").replace("\t","")
    #Converting string date to datetime date
    datePosted = datetime.strptime(soup.find("span", property="datePosted").text.strip()[10:], "%B %d, %Y")

    try:
        advertisedUntil = datetime.strptime(soup.find(property="validThrough").text.strip(), "%Y-%m-%d") #<p> tag
    except:
        advertisedUntil = None

    try:
        baseSalary = soup.find("span", property="baseSalary").text.strip().replace("HOUR","").replace("$$","$").replace("YEAR","").replace("WEEKLY","")
        #Formatting the salary into integers so it can be queried later on (salary is either provided hourly, weekly or yearly)
        if "hourly" in baseSalary:
            salaryType = "hourly"
            if "to" in baseSalary:
                #Take the average of the range
                baseSalary = (float(baseSalary[1:6])+float(baseSalary[11:16]))/2
            else:
                baseSalary = float(baseSalary[1:6])

        elif "weekly" in baseSalary:
            salaryType = "weekly"
            if "to" in baseSalary:
                baseSalary = (float(baseSalary[1:4])+float(baseSalary[9:12]))/2
            else:
                baseSalary = float(baseSalary[1:4])

        elif "monthly" in baseSalary:
            salaryType = "monthly"
            if "to" in baseSalary:
                baseSalary = (float(baseSalary[1:4])+float(baseSalary[9:12]))/2
            else:
                baseSalary = float(baseSalary[1:4])

        elif "yearly" or "annually" in baseSalary:
            salaryType = "yearly"
            if "to" in baseSalary:
                #Take the average of the range
                if len(baseSalary) == 27: #ex: '$38,400 to $40,000 annually'
                    baseSalary = (float(baseSalary[1:7].replace(",",""))+float(baseSalary[12:18].replace(",","")))/2

                elif len(baseSalary) == 28: #ex: '$88,400 to $140,000 annually'
                    baseSalary = (float(baseSalary[1:7].replace(",",""))+float(baseSalary[12:19].replace(",","")))/2

                elif len(baseSalary) == 29: #ex: '$138,400 to $140,000 annually'
                    baseSalary = (float(baseSalary[1:8].replace(",",""))+float(baseSalary[13:20].replace(",","")))/2


            else:
                baseSalary = float(baseSalary[1:7])



    except:
        salaryType = None
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
    logo = findCompanyLogo(company)
    job = Job(title, company, salaryType, baseSalary, workHours, employmentType, location, datePosted, advertisedUntil, jobUrl, logo)
    if containsDescription:
        job.description = description
        job.language = language
        job.educationRequirements = educationRequirements
        job.experienceRequirements = experienceRequirements

    if containsEmploymentGroup:
        job.employmentGroup = employmentGroup

    if containsSpecialCommitments:
        job.specialCommitments = specialCommitments

    uploadToFirebase(job)
    print("job uploaded:", title)



def findCompanyLogo(company):
    try:
        response = clearbit.NameToDomain.find(name=company)
    except:
        return None
    if response == None:
        return None
    else:
        return response["logo"]

def uploadToFirebase(job):
    data = {'title': job.title,
            'company': job.company,
            "salaryType": job.salaryType,
            "baseSalary": job.baseSalary,
            "workHours": job.workHours,
            "location": job.location,
            "specialCommitments": job.specialCommitments,
            "datePosted": job.datePosted,
            "advertisedUntil": job.advertisedUntil,
            "url": job.url,
            "logo": job.logo,
            'description': job.description,
            "language": job.language,
            "educationRequirements": job.educationRequirements,
            "experienceRequirements": job.experienceRequirements,
            "employmentGroup": job.employmentGroup,
            "employmentType": job.employmentType
            }
    db.collection("jobs").document(str(jobId)).set(data)

    #Uploading to firebase

#For testing purposes
# https://www.jobbank.gc.ca/jobsearch/jobposting/32606863
# scrape_job_page("https://www.jobbank.gc.ca/jobsearch/jobposting/32646181")
# scrape_job_page("https://www.jobbank.gc.ca/jobsearch/jobposting/32606884")
# create the session

if __name__ == "__main__":
    for i in range(150):
        with open("/Users/stevengong/Projects/matilda-scrapper/newJobs.json", 'r') as f:
            jobIds = json.load(f)

        jobId = jobIds[0]
        url = "https://www.jobbank.gc.ca/jobsearch/jobposting/" + str(jobId)

        session.run(scrape_job_page)


        with open("/Users/stevengong/Projects/matilda-scrapper/newJobs.json", 'w') as f:
            json.dump(jobIds[1:], f, indent=2)





