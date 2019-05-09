"""
- Pull new patients (X)
    * Creating new patient from scratch
        - Grab random address
        - Generate name / age / ins / gender
        - Assign Buying Pattern ( Look into using neighborhood to help with this )
        - Assign Exam type ( Based on age very loosely )
    * Schedule X patients on using scheduler ( 7 - 14 days ahead )

- Make appointment for a patient. ( Date )
    * Find day in DB
        - Verify date is valid ( Mon - Fri )
        - If invalid, push forward until valid.
    * Find earliest time in DB
        - 30 minute intervals, 10 - 5 pm
        - If full, push date forward one day, and re-verify date is valid.
    * Schedule valid appointment into DB

- Run a single day in system ( Date )
    * Pull all appointments for date. ( Put into list )
        For each patient in list:
        - Check if each will buy something ( Buying pattern )
            > Run quick sale if purchasing
    * Run a check on people who are out of CL's ( Last purchase date vs. CL type ) AND still valid exam.
        For each patient in list:
        - Check if each will buy something ( Buying pattern )
            > Run quick sale if purchasing
    * Run "Life happens" and see if someone needs help ( 1 / 1000 chance )
        ( Try to run per patient, see if cost is too expensive. Patient count, run chance )
        For each patient in list:
        - Check if they need a purchase, or health exam. ( Buying pattern and last exam. Age a factor )
            > Run quick sale if purchasing
            > Run scheduler if needing an exam ( Next open spot )
        - Record into a TXT file. ( Patient had X happen, bought / scheduled )
    * Record events into a CSV / TXT file
        - Total appointments that day, and total sales that day.
    * Schedule return patient exams
        - Look at all patients that are 10 days out from one year exam. ( CL patients / insurance higher chance )
            > Based on buying pattern, schedule.
        - Look at all patients that are 30 / 60 / 90 days past one year exam.
            > Based on reducing chance, schedule.
        - Look at all patients that are 10 days from two year exam. ( Glasses patients higher chance )
            > Based on buying pattern, schedule.
        - Look at all patients that are 30 / 60 / 90 days past two year exam.
            > Based on buying pattern, schedule.
        - Else: Patient lost / gone.


- Have a file separate for buying pattern logic
    * CSV file? - No
    * Dictionary * patient_logic.py (JSON Style with some functions included)
"""

import random
from datetime import datetime, timedelta, date, time
from SQL.postgresqlcommands import DBCommands
from SQL.sales_inserter import InsertItem
from . import patient_logic as plogic   # All of the logic that drives the automation
from .product_logic import ProductPurchase


class NewPatient(object):
    """
    Takes new patients and inserts them into the schedule. If patient does not have proper info,
    (Buying pattern, exam type) then it will fill those in. If no new patient exists, it will create one from scratch.
    Logic in a separate file for easier editing.
    """
    def __init__(self, number, current_day=None):
        self.number = number
        self.current_day = current_day if current_day else date.today()
        self.db = DBCommands()
        self.db.connect()

    def __del__(self):
        self.db.commit_close()

    def patient_selector(self):
        # self.db.connect()
        new_patients = self.db.view_free("SELECT patients.id, patients.age FROM patients WHERE NOT "
                                         "EXISTS(SELECT patient FROM schedule WHERE patients.id=schedule.patient)",
                                         slow=False)     # Pull all patients that have never been seen.

        while len(new_patients) < self.number:
            self.create_patient()
            # TODO Append new patient_id to the new_patients list
            print("Not enough patients to add to scheduler.")
            break

        selected_patients = random.sample(new_patients, self.number)
        for patient in selected_patients:
            patient_id = patient[0]
            age = patient[1]
            info = self.db.view('auto_patient', field="buying_pattern, exam_type",
                                conditional=["patient_id", patient_id], slow=False)
            # Check if patient exists in auto_table
            if len(info) == 0:    # If patient not in auto patient
                buying_pattern = plogic.create_buying_pattern()
                exam_type = plogic.create_exam_type(age)
                rx_str = plogic.create_rx_strength()
                self.db.insert(["auto_patient", ("patient_id", patient_id), ("buying_pattern", buying_pattern),
                                ("exam_type", exam_type), ("rx_strength", rx_str)], slow=False)
                insurance = plogic.create_insurance_type()
                self.db.update(['patients', ('insurance', insurance), ('id', patient_id)], slow=False)
                days_out = random.randint(7, 14)    # Set date for week to two weeks
                sch = Scheduler(patient_id, days_out, self.current_day)
                sch.schedule_patient()      # Put patient on schedule
            else:
                days_out = random.randint(7, 14)  # Set date for week to two weeks
                sch = Scheduler(patient_id, days_out, self.current_day)
                sch.schedule_patient()  # Put patient on schedule
        # self.db.commit_close()

    def create_patient(self):  # TODO Finish this.
        # Create patient from scratch, calling all other info. ( Maybe turn into its own class / file )
        # Eventually this will also auto make buying pattern and exam type as well. ( Full patient creation )
        pass


class Scheduler(object):
    """
    Takes patient and will schedule them in an appropriate time slot.
    """
    def __init__(self, patient_id, days_out, current_date=None):
        self.patient_id = patient_id
        self.current_date = current_date if current_date else date.today()
        self.exam_date = self.days_to_date(days_out)    # Date desired for appointment ( 02/05/2019 )
        self.initial_exam_date = self.days_to_date(days_out)
        self.db = DBCommands()
        self.db.connect()   # Connect this class to DB
        self.days = plogic.working_days
        self.time = plogic.business_hours
        self.appt_time = plogic.appt_slot

    def __del__(self):
        self.db.commit_close()

    def schedule_patient(self):
        self.date_is_valid()
        appt_time = self.time_is_valid()
        try:
            self.db.insert(['schedule', ('patient', self.patient_id), ('appt_date', self.exam_date),
                            ('appt_time', appt_time)], slow=False)
        except Exception:
            self.db.rollback()
        else:
            with open('Appointments.txt', 'a') as file:
                file.write(f"Patient {self.patient_id} was scheduled on {self.exam_date}, which is {self.date_difference()}"
                           f" days from initial appointment date.\n")     # For record purposes.

    def days_to_date(self, days_out):
        return self.current_date + timedelta(days_out)

    def date_is_valid(self):
        valid = False
        while not valid:
            if self.exam_date.weekday() in self.days:   # If date is listed as open in self.days
                valid = True
            else:
                self.exam_date += timedelta(1)          # Advance forward one day

    def time_is_valid(self):
        valid = False
        while not valid:
            appointments = self.db.view_schedule(self.exam_date)
            if len(appointments) == 0:  # No appointments on that day.
                appt_time = [self.time[0], 0]   # Book earliest appointment
                return time(appt_time[0], appt_time[1])
            else:
                latest_hour = str(appointments[-1][2]).split(":")[0]
                latest_minute = str(appointments[-1][2]).split(":")[1]
                appt_time = [int(latest_hour), int(latest_minute) + self.appt_time]   # Set next appointment
                if appt_time[1] >= 60:
                    appt_time[0] += 1   # Goto next hour.
                    appt_time[1] -= 60
                if appt_time[0] >= self.time[1]:    # Past work time
                    self.exam_date += timedelta(1)  # Try next day
                    self.date_is_valid()            # Make sure it's a business day
                else:
                    return time(appt_time[0], appt_time[1])
        # self.db.conn.close()
        # Check for earliest time available for date. ( 10 - 5 , in 30 minute intervals )
        # If full, add a day and run date_is_valid again.

    def date_difference(self):
        difference = str(self.exam_date - self.initial_exam_date)
        if "," in difference:
            return int(difference.split(" ")[0])    # Get difference in days
        else:
            return 0    # Same day appointment


class ProcessWorkDay(object):
    """
    Does the work of running through each patient on that days schedule, deciding purchases, events and rescheduling.
    """
    def __init__(self, work_date):
        self.work_date = work_date
        self.work_day = self.is_valid()
        self.next_valid_day = None
        self.db = DBCommands()
        self.ii = InsertItem()
        self.db.connect()

    def __del__(self):
        self.db.commit_close()

    def is_valid(self):
        if self.work_date.weekday() in plogic.working_days:
            return True     # Used for sales that are outside of working days, such as medical or glasses broke.
        else:
            return False

    def process_day(self):      # TODO Work on this!
        if self.work_day:
            self.ii.db.connect()
            patients = self.db.view_schedule(self.work_date)
            patient_list = []
            for patient in patients:    # Seems messy, maybe easier way to do this?
                patient_list.append(patient[1])
            for patient in patient_list:
                insurance = self.db.view('patients', conditional=('id', patient), field='insurance', slow=False)[0][0]
                auto_patient = self.db.view('auto_patient', ('patient_id', patient), slow=False)
                if len(auto_patient) == 0:
                    print(f"Patient {patient} not in auto_patient.")    # Trying to catch a bug
                else:
                    auto_product = ProductPurchase(auto_patient[0][1])  # Get id of patient
                    auto_product.run_sale()
                    purchase_list = auto_product.purchases
                    if len(purchase_list) > 0:
                        self.ii.quick_sale(patient, self.work_date, insurance, purchase_list)
                        last_purchases = plogic.last_purchase(purchase_list)
                        for item in last_purchases:     # Something here is not working, insert test?
                            self.db.cmd_free(f"UPDATE auto_patient SET {item} = '{self.work_date}' "
                                             f"WHERE patient_id = {patient}", slow=False)
                        first = self.db.view('patients', ('id', patient), field='first_purchase', slow=False)[0][0]
                        if first is None or first > self.work_date:
                            self.db.cmd_free(f"UPDATE patients SET first_purchase = '{self.work_date}' "
                                             f"WHERE id = {patient}", slow=False)

            self.db.conn.commit()   # Separate connections
            self.ii.db.commit_close()

    def check_future_appointments(self):
        for day in plogic.dates:
            back_date = self.work_date - timedelta(day)
            previous_patients = self.db.view('auto_patient', conditional=('last_exam_date', back_date), slow=False)
            for patient in previous_patients:
                _, patient_id, buying_pattern, exam_type, last_exam, last_glasses, last_contacts, rx_str = patient
                insurance = self.db.view('patients', field='insurance',
                                         conditional=('id', patient_id), slow=False)[0][0]
                has_insurance = False
                if insurance in plogic.insurances:
                    has_insurance = True
                schedule = plogic.schedule(int(buying_pattern), exam_type, day, has_insurance)
                if schedule:
                    days_out = random.randint(7, 14)
                    sch = Scheduler(patient_id, days_out, self.work_date)
                    sch.schedule_patient()

    def life_happens(self):
        # Use a separate file for logic
        # Go through patients, and see if any need special help
        # If so, run scheduler or sale based on need.
        # If not valid work day, then sale on next valid day ( automatically )
        # Record events ( Just for testing )
        pass

    def check_contacts(self):
        # Look through DB for all people who are overdue for CL's ( Look at last sale date, and CL type, times # boxes)
        # Check if exam is valid ( under a year )
        # if exam valid: Based on buying pattern, purchase new CL's
        # if exam not valid: Schedule new exam
        # Make sure date is valid
        pass

    def record_day(self):
        self.db.connect()
        totals = self.db.view('sale', conditional=('purchase_time', self.work_date), slow=False)
        patients = len(totals)
        total_dollar = 0
        for person in totals:
            total_dollar += person[3]
        with open('Daily_totals.txt', 'a') as file:
            file.write(f"On {self.work_date} there was {patients} "
                       f"scheduled and we earned ${total_dollar/100}.\n")

    def run_day(self):  # Puts everything together in order.
        self.process_day()
        self.check_future_appointments()
        self.record_day()

