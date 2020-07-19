# I cannot seem to make this work
from crontab import CronTab
cron = CronTab(user=True)
job = cron.new(command='/opt/miniconda3/bin/python /Users/stevengong/Projects/matilda-scrapper/jobBankSpecificJob.py')
job.minute.every(10)

#Run job every 24 hours
# job2 = cron.new(command='/opt/miniconda3/bin/python /Users/stevengong/Projects/matilda-scrapper/jobBankSearch.py')
# job2.hour.every(24)

cron.write()

# import schedule
# import time
#
# from jobBankSpecificJob import scrape_job_page
# from test import test
# schedule.every(1).seconds.do(scrape_job_page)
# # schedule.every().hour.do(job)
# # schedule.every().day.at("10:30").do(job)
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)