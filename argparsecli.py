from jobBankSearch import scrapeJob
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='Job scrapping CLI from JobBank Canada.')
    parser.add_argument('--searchString', type=str, default="",
                        help='The name of the job you are looking for')
    parser.add_argument('--prov', type=str, default="",
                        help='The province you would like to find your job in')
    args = parser.parse_args()
    print(str(listJobs(args)))



#https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=software+developer
def listJobs(args):
    base_url = "https://www.jobbank.gc.ca/jobsearch/jobsearch?"
    searchString = "searchstring=" + args.searchString
    province = "&fprov="+ args.prov
    search = base_url +searchString + province
    print(search)
    scrapeJob(search)

if __name__ == "__main__":
    main()