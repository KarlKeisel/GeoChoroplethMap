from automatic.auto_patient import *
from SQL.postgresqlcommands import DBCommands
from collections import Counter
from datetime import datetime, timedelta, date, time
import pytest
from unittest import mock
from automatic import patient_logic as plogic


# pytest -v -p no:warnings

# db = DBCommands()
# np = NewPatient(2)
# # #
# np.db.connect()
# np.patient_selector()
# np.db.commit_close()

#
# auto_pat = db.view('auto_patient')
# print(auto_pat)
# sch_pat = db.view('schedule', command=('appt_date >', date(2019, 4, 1)))
# print(sch_pat)
#
# # products = db.view('products', slow=False)
# # print(products)

# with open('Appointments.txt', 'r') as file:
#     text = file.readlines()
# print(*text)
# open('Appointments.txt', 'w').close()

"""
NewPatient Test

Not quite sure how to run a test driven program to check this. Random patients, random dates. Mock?
"""

"""
Test patients, 100, 101, 102 Scheduled on 02/20/2014 and 102 also on 02/21/2014

Scheduler Test
"""


@pytest.fixture()
def setup_scheduler():
    patient_id = 103
    days_out = 10
    current_date = date(2014, 2, 20)
    sample_schedule = Scheduler(patient_id, days_out, current_date)
    return sample_schedule


def test_schedule_patient(setup_scheduler):

    sch = setup_scheduler
    sch.exam_date = date(2014, 2, 19)
    sch.schedule_patient()
    schedule = sch.db.view('schedule', conditional=('patient', 103), slow=False)
    assert len(schedule) != 0
    sch.db.delete('schedule', ('patient', 103), slow=False)


def test_days_to_date(setup_scheduler):
    schedule = setup_scheduler
    assert schedule.current_date == date(2014, 2, 20)
    assert schedule.exam_date == date(2014, 3, 2)
    assert schedule.days_to_date(8) == date(2014, 2, 28)
    assert schedule.days_to_date(-1) == date(2014, 2, 19)


def test_date_is_valid(setup_scheduler):
    sch = setup_scheduler
    sch.exam_date = date(2014, 2, 20)
    sch.date_is_valid()
    assert sch.exam_date == date(2014, 2, 20)   # Thursday
    sch.exam_date = date(2014, 2, 22)   # Saturday
    sch.date_is_valid()  # Should move to next valid date ( Currently Monday )
    assert sch.exam_date == date(2014, 2, 24)


def test_time_is_valid(setup_scheduler):
    sch = setup_scheduler
    sch.db.connect()
    t_time = sch.time_is_valid()
    assert t_time == time(10, 0)    # 1st appointment on March 2nd, 2014
    sch.exam_date = date(2014, 2, 20)
    t_time = sch.time_is_valid()
    assert t_time == time(11, 30)    # 3 appointments ahead
    sch.exam_date = date(2014, 2, 21)   # Friday has appointment at very last slot
    t_time = sch.time_is_valid()
    assert t_time == time(10, 0)
    assert sch.exam_date == date(2014, 2, 24)   # Monday


def test_date_difference():
    sch = Scheduler(103, 10, date(2014, 2, 20))
    e_time = sch.date_difference()
    assert e_time == 0      # Initial exam scheduled on day patient wanted
    sch.exam_date = date(2014, 3, 30)
    e_time = sch.date_difference()
    assert e_time == 28     # 28 days from 2014, 3, 2
    sch.exam_date = date(2014, 2, 20)
    e_time = sch.date_difference()
    assert e_time == -10


# exam_date2 = date(2014, 2, 23)  # Saturday
#
# sch = Scheduler(103, 10, exam_date2)  # Set up patient # 103 for test day.

# test_date = date(2014, 2, 20)
# sch = Scheduler(30, 4, test_date)
# # print(sch.exam_date, sch.initial_exam_date)
# test_date2 = date(2014, 2, 22)
#
# # print(int(str(test_date - test_date2).split(" ")[0]))
# times = time(10, 0)
# time2 = "10:00"


"""
ProcessWorkDay Tests
"""


@pytest.fixture()
def setup_workday():
    work_date = date(2014, 2, 20)       # Thursday
    workday = ProcessWorkDay(work_date)
    return workday


def test_is_valid(setup_workday):
    workday = setup_workday
    assert workday.work_day is True
    workday.work_date = date(2014, 2, 23)   # Sunday
    workday.work_day = workday.is_valid()
    assert workday.work_day is False


def test_process_day(setup_workday):    # Patient list should be 100, 101, 102
    workday = setup_workday
    workday.process_day()
    workday.db.connect()
    sales = workday.db.view('sale', conditional=('purchase_time', date(2014, 2, 20)), slow=False)
    assert len(sales) != 0
    workday.db.delete('sale', ('purchase_time', date(2014, 2, 20)), slow=False)


wd = ProcessWorkDay(date(2014, 2, 20))
wd.process_day()
wd.db.connect()
wd.record_day()
