"""
Runs nightly and updates all data for the next day.
Checks sales, updates patient's data, updates geocoordinates, updates choropleth map.
"""

# TODO Set up auto update at 3 am
# TODO Check all sales for yesterday and update average dollar and most recent purchase timestamp
# TODO Verify if patient is new, or old patient. (Observer Object?)
# TODO Check patient DB for any addresses without lat or lon and attempt to look them up and append to DB
# TODO Run choropleth map maker to update the data of the new patients. (May have to figure out a faster way to do it)

from SQL.postgresqlcommands import DBCommands
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime as dt
from automatic.auto_patient import *

sched = BlockingScheduler()

# Samples


@sched.scheduled_job('interval', seconds=5)
def timed_job():    # Tester
    date = dt.date
    print('Updating patient information. ' + dt.datetime.now().strftime("%I:%M:%S %p"))
    print('Entering new patients.' + dt.datetime.now().strftime("%I:%M:%S %p"))
    print('Entering new sales.' + dt.datetime.now().strftime("%I:%M:%S %p"))
    print('Running address geocoordinates on unknown addresses.' + dt.datetime.now().strftime("%I:%M:%S %p"))
    print('Updating map with new information.' + dt.datetime.now().strftime("%I:%M:%S %p"))
    print('Finished updating.' + dt.datetime.now().strftime("%I:%M:%S %p"))

# @sched.scheduled_job('cron', day_of_week='mon-fri', hour=3)
# def scheduled_job():
#     print('This job is run every weekday at 3am.')


@sched.scheduled_job('cron', day_of_week='sun-sat', hour=3)
def scheduled_job():
    date = dt.date
    print('Updating patient information. ' + dt.datetime.now().strftime("%I:%M:%S %p"))
    print('Processing new sales.' + dt.datetime.now().strftime("%I:%M:%S %p"))
    wd = ProcessWorkDay(date)
    wd.run_day()
    print('Scheduling new patients.' + dt.datetime.now().strftime("%I:%M:%S %p"))
    np = NewPatient(2, date)
    np.patient_selector()
    print('Updating map with new information.' + dt.datetime.now().strftime("%I:%M:%S %p"))
    # TODO Run map maker
    print('Finished updating.' + dt.datetime.now().strftime("%I:%M:%S %p"))


sched.start()

