"""
Logic for each buying pattern and odds that events occur. Trying dictionary to reduce importing csv files and should
allow for growth of the tables without increasing the processing time by much.
"""
import numpy as np
import random


def age_round(age):
    if age > 80:
        return 80
    if age < 10:
        return 10
    while age % 10 != 0:
        age += 1
    return age


def create_buying_pattern():
    y = int(np.random.normal(3.3, 1.2))
    while y < 1 or y > 5:
        y = int(np.random.normal(3.3, 1.2))  # Re-roll until within 1 - 5
    return y


def create_rx_strength():   # General strength of Rx, 0 means very light, not none.
    y = int(np.random.normal(-1, 3))
    return y


def create_exam_type(age):
    logic_age = age_round(age)
    exam_chance = exam_type[logic_age]
    chance = random.randint(1, 10)
    chance -= exam_chance[0]
    if chance > 0:
        chance -= exam_chance[1]
        if chance > 0:
            return 'Health'
        else:
            return 'Contacts'
    else:
        return 'Glasses'


def create_insurance_type():
    chance = random.randint(1, 10)  # SQL Update seems to need the double "'str'" to work.
    if chance < 4:
        return "'None'"
    if chance < 5:
        return "'Poor'"
    if chance < 9:
        return "'Standard'"
    else:
        return "'Good'"


def purchase_list(auto_patient):
    purchases = []
    _, patient_id, buying_pattern, exam_type, last_exam, last_glasses, last_contacts, rx_str = auto_patient
    # Exam Purchases
    if exam_type == 'Health':
        # TODO Buying_pattern logic and stuff
        purchases.extend([5, 8, 9])
    elif exam_type == 'Contacts':
        # TODO Buying_pattern logic
        purchases.extend([1, 5, 6, 9])
    else:
        # TODO Buying_pattern logic
        purchases.extend([1, 5])
    # Stuff Purchases
    if exam_type == 'Health':
        pass
    elif exam_type == 'Contacts':
        purchases.extend([26, 26, 26, 26, 12, 13, 19, 21])
    else:
        purchases.extend([11, 19, 23, 24])
    return purchases


def last_purchase(purchases):
    purchased = set()
    for item in purchases:
        if item in glasses:     # Name of tables in auto_patient
            purchased.add("last_glasses_purchase_date")
        elif item in contacts:
            purchased.add("last_cl_purchase_date")
        elif item in exam:
            purchased.add("last_exam_date")
        else:   # Added in case of future items added.
            pass
    return purchased


# Last Purchase info
glasses = {10, 11, 12, 18, 19, 20}
contacts = {26, 27, 28}
exam = {1, 5, 6, 7, 8}

# Insurances
insurances = {'Poor', 'Standard', 'Good'}   # List of all insurances taken.

# Work days
working_days = (0, 1, 2, 3, 4)  # Open on weekdays

# Business Hours (24 hour clock)
business_hours = (10, 17)

# Appointment time slots ( How long per appointment )
appt_slot = 30

# Exam type logic:  {Age : [Glasses, Contacts, Health]}
exam_type = {10: [9, 0, 1], 20: [5, 4, 1], 30: [6, 3, 1], 40: [6, 3, 1], 50: [6, 2, 2], 60: [6, 1, 3],
             70: [5, 1, 4], 80: [4, 1, 5]}

# Buying pattern logic: Pattern = {Exam_type : {Age : [

buying_5 = {'Glasses': {10: []}}

# Scheduling pattern logic = {Pattern : {exam_type : {days_out : [% Chance to appt, % chance to appt w/ ins]}}
dates = [365, 395, 425, 730, 760, 790]  # Used to easily look at dates for new exams
schedule_logic = {5: {'Glasses': {365: [90, 93], 395: [50, 70], 425: [20, 30], 730: [40, 20], 760: [20, 10], 790: [5, 5]},
                      'Contacts': {365: [95, 95], 395: [60, 80], 425: [10, 15], 730: [20, 10], 760: [2, 2], 790: [1, 1]},
                      'Health': {365: [90, 93], 395: [50, 70], 425: [10, 15], 730: [20, 10], 760: [2, 2], 790: [1, 1]}},
                  4: {'Glasses': {365: [75, 85], 395: [40, 70], 425: [20, 30], 730: [50, 20], 760: [25, 10], 790: [5, 5]},
                      'Contacts': {365: [85, 85], 395: [50, 80], 425: [10, 15], 730: [25, 10], 760: [2, 2], 790: [1, 1]},
                      'Health': {365: [80, 83], 395: [35, 55], 425: [5, 10], 730: [10, 5], 760: [2, 2], 790: [1, 1]}},
                  3: {'Glasses': {365: [60, 70], 395: [35, 55], 425: [5, 15], 730: [60, 70], 760: [30, 15], 790: [8, 8]},
                      'Contacts': {365: [65, 75], 395: [35, 55], 425: [15, 15], 730: [40, 60], 760: [30, 15], 790: [1, 1]},
                      'Health': {365: [55, 70], 395: [20, 40], 425: [15, 15], 730: [30, 50], 760: [15, 5], 790: [1, 1]}},
                  2: {'Glasses': {365: [20, 30], 395: [20, 30], 425: [15, 15], 730: [60, 70], 760: [30, 15], 790: [1, 1]},
                      'Contacts': {365: [20, 40], 395: [10, 20], 425: [5, 5], 730: [60, 70], 760: [30, 30], 790: [1, 5]},
                      'Health': {365: [17, 35], 395: [10, 15], 425: [5, 7], 730: [50, 60], 760: [15, 15], 790: [5, 5]}},
                  1: {'Glasses': {365: [15, 25], 395: [15, 25], 425: [10, 10], 730: [60, 70], 760: [40, 25], 790: [10, 10]},
                      'Contacts': {365: [15, 25], 395: [15, 25], 425: [10, 10], 730: [70, 80], 760: [50, 35], 790: [15, 15]},
                      'Health': {365: [10, 20], 395: [10, 20], 425: [5, 8], 730: [55, 60], 760: [40, 40], 790: [15, 20]}}}


def schedule(buying_pattern, exam_type, days_out, insurance):
    chance = random.randint(1, 100)
    has_insurance = 1 if insurance else 0
    chance -= schedule_logic[buying_pattern][exam_type][days_out][has_insurance]
    if chance > 0:
        return False
    else:
        return True

# Life happens logic:

# Exam scheduling logic: Pattern = {Exam_type : {Date_previous_exam : [Days_out : % Chance]}}
# 5 Buying pattern, kid 10 years old, glasses. Will buy 1 - 2 pairs. One fancy, and another fancy, or safe pair.
# Pattern, exam_type, age, % Glasses purchased, glasses types

# TODO Find a way to look at old purchases, very useful for the every other year people.
