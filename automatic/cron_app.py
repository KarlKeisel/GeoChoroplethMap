"""
Runs nightly and updates all data for the next day.
Checks sales, updates patient's data, updates geocoordinates, updates choropleth map.
"""

# TODO Run choropleth map maker to update the data of the new patients. (May have to figure out a faster way to do it)

from apscheduler.schedulers.blocking import BlockingScheduler
import datetime as dt
from automatic.auto_patient import *
from map_data.choropleth_maker import *

sched = BlockingScheduler()


@sched.scheduled_job('interval', seconds=5)
def timed_job():    # Tester
    today_date = dt.date
    print('Updating patient information. ' + dt.datetime.now().strftime("%I:%M:%S %p"))
    print('Entering new patients.' + dt.datetime.now().strftime("%I:%M:%S %p"))
    print('Entering new sales.' + dt.datetime.now().strftime("%I:%M:%S %p"))
    print('Running address geocoordinates on unknown addresses.' + dt.datetime.now().strftime("%I:%M:%S %p"))
    print('Updating map with new information.' + dt.datetime.now().strftime("%I:%M:%S %p"))
    print('Finished updating.' + dt.datetime.now().strftime("%I:%M:%S %p"))


@sched.scheduled_job('cron', day_of_week='mon-sun', hour=3)
def scheduled_job():
    today_date = dt.date
    print('Updating patient information. ' + dt.datetime.now().strftime("%I:%M:%S %p"))
    print('Processing new sales.' + dt.datetime.now().strftime("%I:%M:%S %p"))
    wd = ProcessWorkDay(today_date)
    wd.run_day()
    print('Scheduling new patients.' + dt.datetime.now().strftime("%I:%M:%S %p"))
    np = NewPatient(2, today_date)
    np.patient_selector()
    print('Updating map with new information.' + dt.datetime.now().strftime("%I:%M:%S %p"))
    update_map()
    with open('updated.txt', 'w') as f:
        f.write(dt.datetime.now().strftime("%a %d, %Y"))
    print('Finished updating.' + dt.datetime.now().strftime("%I:%M:%S %p"))


sched.start()
