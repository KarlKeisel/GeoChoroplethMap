import numpy as np
import pandas as pd
import random

"""
Creates dummy patient data using a formula to make a purchasing pattern.

Will be used to simulate the office through a day to day pattern. Will be called nightly using the cron_updater.py.
"""

"""
Start purchase date of a patient: (Maybe 2 patients a day)
Which insurance do they have? (Worry about discounts later, insurance still counts as paid)
Which exam that day? (Regular, CL's, Health)
Buys glasses that day? More than one? Contacts? (Chance based on exam type)
Type of glasses / CL's? (Based on pattern)
Chance they buy glasses outside of exam? (Based on buying pattern, very small)
When do they see next appointment? (12-24 for exam, 12ish for CL's, 6ish for Health based on buying pattern)
If health exam, do they need a refraction? (12ish months)
Do they need new glasses? (Based on buying pattern)
Advance calendar forwards.
"""

# Buying Patterns
"""
5 : Exam every year, if contacts will still buy glasses as well, if glasses, will buy multiple.
4 : Exam every year, will buy year supply of CL's with glasses every other year, glasses every year if not.
3 : Exam every year (Mostly), most likely will by CL's (6 month or so) glasses rare, or glasses every year - 2 years.
2 : Exam every other year, might buy 3 months CL's, or glasses every other year.
1 : Exam every other year, often buying nothing but exam.
"""


class Patient(object):

    patient_list = []   # Keep track of all patients who are purchasing. Possibly a bad idea once it grows too big.
    # Or just look at DB every 'day' that passes.

    def __init__(self, patient_id, buying_pattern=None):
        self.patient_id = patient_id
        self.buying_pattern = buying_pattern if buying_pattern else self.create_buying_pattern()
        self.patient_type = self.set_patient_type
        self.last_exam = None
        self.last_health_exam = None
        Patient.patient_list.append(self.patient_id)    # Maybe not needed.

    def set_patient_type(self):
        x = random.randint(1, 10)   # Set up if glasses, cl's, health as main.
        if x > 5:
            self.patient_type = 'glasses'
        elif x > 2:
            self.patient_type = 'contacts'
        else:
            self.patient_type = 'health'
        # TODO Set insurance as well under patient file

    @staticmethod
    def create_buying_pattern():
        y = int(np.random.normal(3.3, 1.2))
        while y < 1 or y > 5:
            y = int(np.random.normal(3, 1.2))
        return y

    def set_appointment(self):  # Set appointment and just start from early and go to latest, next day if full.
        pass

    def purchase(self):  # Look at age before choosing purchase
        pass

    def will_patient_purchase(self):  # Look at last purchase, and patient type
        pass

    def will_patient_appointment(self):  # Look at last exam date, and patient type. Set appointments ~ 20 days in adv.
        pass

    def set_appointment_time(self):    # Will make sure appointment is valid.
        pass

    def set_new_appointment(self):     # Will add new patients to appointment times.
        pass

    def decide_purchase_type(self):    # Will decide what to buy when patient purchases.
        pass

    def life_event(self):  # Will determine if they need to be seen between exams.
        """
        Glasses: Lost, stolen, or broken. Young age will make more likely. Buying type will determine what they get.

        Contact Lenses: Over wearing them. Young age and low buying pattern more likely. Look at last glasses purchase
            as well as setting up a health appointment. Might need new glasses. (Cheap)
        """
        pass

    def update(self, date):  # The automated part that puts everything into action
        pass
