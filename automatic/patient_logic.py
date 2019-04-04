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


def purchase_list(auto_patient):
    purchases = []
    _, buying_pattern, buying_pattern, exam_type, last_exam, last_glasses, last_contacts, rx_str = auto_patient
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

# Life happens logic:

# Exam scheduling logic: Pattern = {Exam_type : {Date_previous_exam : [Days_out : % Chance]}}
# 5 Buying pattern, kid 10 years old, glasses. Will buy 1 - 2 pairs. One fancy, and another fancy, or safe pair.
# Pattern, exam_type, age, % Glasses purchased, glasses types

# TODO Find a way to look at old purchases, very useful for the every other year people.
