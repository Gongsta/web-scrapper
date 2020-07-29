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


def findCompanyLogo(company):
    try:
        response = clearbit.NameToDomain.find(name=company)
    except:
        return None
    if response == None:
        return None
    else:
        return response["logo"]

def uploadToFirebase(job,id):
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
    db.collection("jobs").document(id).set(data)


def testing():
    with open("/Users/stevengong/Projects/matilda-scrapper/test.txt", 'w') as f:
        f.write("helllo world")