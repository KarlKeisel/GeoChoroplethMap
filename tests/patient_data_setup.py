import numpy as np
import pandas as pd
import random

"""
Creates dummy patient data using a formula to make a purchasing pattern.
"""

# Buying patterns (1, 2, 3, 4, 5) with 5 being big spender.

# TODO Set up trigger to get average dollar sale.

# TODO Create a formula for determining the following:
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

y = pd.DataFrame(np.random.normal(3, 1.2, 50))
print(y)


class Patient(object):

    patient_list = []   # Keep track of all patients who are purchasing. Possibly a bad idea once it grows too big.

    def __init__(self, patient_id, buying_pattern):
        self.patient_id = patient_id
        self.buying_pattern = buying_pattern
        self.patient_type = self.set_patient_type
        self.last_exam = None
        self.last_health_exam = None
        Patient.patient_list.append(self.patient_id)

    def set_patient_type(self):
        x = random.randint(1, 10)   # Set up if glasses, cl's, health as main.
        if x > 5:
            self.patient_type = 'glasses'
        elif x > 2:
            self.patient_type = 'contacts'
        else:
            self.patient_type = 'health'

    def first_purchase(self):
        pass
