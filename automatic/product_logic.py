"""
Used to process any product purchases.

Will use previous (if any) data as well as buying patterns to help decide what the patient will purchase.
Will return list of numbers that will relate to id of products in DB.
Exams handled under patient logic.

*** Updates to DB products WILL break this.
"""

import time
import numpy as np
import random
from datetime import date
from SQL.postgresqlcommands import DBCommands

# TODO System to take in old purchase data, sort into each date of purchases.
# TODO System to take in buying patterns, age, gender, rx str, purchase type.

# TODO System to break down each product piece. (Frame, lenses, contacts)
# TODO Take everything and combine it into a single list of purchases, return that list.


class ProductPurchase(object):

    def __init__(self, patient):
        self.patient = patient
        self.db = DBCommands()
        self.db.connect()
        self.purchases = []     # This will be what is used for sales. Empty list will mean no purchase.
        self.patient_demographics = None  # Pulled from "patients" table
        self.patient_auto = None    # Pulled from "auto_patient" table
        self.patient_history = None  # Pulled from "sale_item" table. Will need to have dates from "sale" table also.
        self.patient_history_dates = []  # Date of each sale
        self.patient_insurance = (0, 'None')   # Separated to allow easier indexing.
        self.product_list = None

    def __del__(self):
        self.db.conn.close()    # Nothing will be recorded in DB

    def pull_product_list(self):
        i = self.db.view('products', field='id, product', slow=False)
        self.product_list = i

    def pull_patient_demographics(self):
        i = self.db.view('patients', field='id, insurance, age, gender', conditional=('id', self.patient), slow=False)
        self.patient_demographics = i[0]

    def pull_patient_auto(self):
        i = self.db.view('auto_patient', conditional=('patient_id', self.patient), slow=False)
        self.patient_auto = i[0][1:]

    def pull_patient_history(self):
        i = self.db.view_free(f"SELECT sale_item.product_id, sale.purchase_time FROM sale_item INNER JOIN "
                              f"sale ON sale_item.sale_id = sale.id WHERE sale.patient = {self.patient}", slow=False)
        if len(i) > 0:  # If there is a history
            self.patient_history = {}   # Change to dictionary
            dates = set()
            for item in i:  # Pull dates from data
                dates.add(item[1])
            self.patient_history_dates = list(dates)
            self.patient_history_dates.sort()
            for day in self.patient_history_dates:
                items = []
                sales = [x for x in i if x[1] == day]   # Sort by dates to prevent massive list iterations
                for item in sales:  # Pull sales data
                    items.append(item[0])
                    self.patient_history[day] = items

    def pull_patient_data(self):   # Created to allow multiple ways to pull data in future if needed.
        self.pull_patient_demographics()
        self.pull_patient_auto()
        self.pull_patient_history()
        self.set_insurance()

    def run_sale(self):
        self.pull_patient_data()
        self.pull_product_list()
        self.purchases = []  # Reset purchase list to prevent doubles
        self.purchase_exam()
        self.purchase_contacts()
        count = self.purchase_glasses()
        if count > 0:
            self.purchases += self.glasses_type(count)

    def set_insurance(self):
        if self.patient_demographics:
            found = False
            patient_insurance = self.patient_demographics[1]
            for i in enumerate(insurance):
                if patient_insurance == i[1]:
                    self.patient_insurance = i
                    found = True
            if not found:
                self.patient_insurance = (0, 'None')

    def purchase_exam(self):   # Used to populate exam ids, needs to run first.
        if self.patient_auto[2] == 'Health':
            self.purchases += [8, 5]

        elif self.patient_auto[2] == 'Contacts':
            if self.patient_history:
                found = False
                for i in reversed(self.patient_history_dates):  # Dictionary Date: [purchases]
                    if 6 in self.patient_history[i]:
                        self.purchases += [1, 5, 6]
                        found = True
                        break  # Stop after first found
                    elif 7 in self.patient_history[i]:
                        self.purchases += [1, 5, 7]
                        found = True
                        break
                if not found:
                    self.first_cl_exam()
            else:
                self.first_cl_exam()

        else:  # Glasses purchase
            self.purchases += [1, 5]

        # Check for optimap purchase
        count = 0
        if self.patient_history:
            for i in reversed(self.patient_history_dates):
                if count > 3 or count < -3:
                    break
                if 9 in self.patient_history[i]:
                    count += 1
                else:
                    count -= 1
        chance = random.randint(1, 50) + (loyal_optimap * count) + optimap[int(self.patient_auto[1])]
        if chance >= 30:
            self.purchases += [9]

    def first_cl_exam(self):
        chance = random.randint(1, 100)
        exam_type = cl_exam_type
        if self.patient_demographics[2] >= 40:
            age = self.patient_demographics[2] - 30
            special_fit = int(age / 10) * cl_age_factor
            exam_type -= special_fit
        if chance >= cl_exam_type:
            self.purchases += [1, 5, 7]
        else:
            self.purchases += [1, 5, 6]

    def pick_contacts(self):
        contact_type = None
        chance = random.randint(1, 100)
        for i in type_contacts:
            if chance <= type_contacts[i][int(self.patient_auto[1])]:
                contact_type = i
                break
            else:
                chance -= type_contacts[i][int(self.patient_auto[1])]
        return contact_type

    def purchase_contacts(self):
        if self.patient_auto[2] != 'Contacts':
            return None
        contact_type = None
        if self.patient_history:
            contacts = {26, 27, 28}
            count = 0
            for i in reversed(self.patient_history_dates):
                if contact_type is None:
                    contact_type = contacts.intersection(self.patient_history[i])
                    pass
                if contacts.intersection(self.patient_history[i]) == contact_type:
                    count += 1
                else:
                    break   # Stop looking after patient switched type
                if count >= abs(switch_contacts[1] / switch_contacts[0]):
                    break   # Stop looking after 0 % switch chance
            switch_chance = switch_contacts[1] - (switch_contacts[0] * count)
            if len(contact_type) > 0:
                contact_type = self.product_id(list(contact_type)[0], to_id=False)  # Pull CL name
            else:
                contact_type = self.pick_contacts()
            if switch_chance > 0:
                chance = random.randint(1, 100)
                if chance < switch_chance:
                    contact_type = self.pick_contacts()

        else:
            contact_type = self.pick_contacts()
        if contact_type is None:
            raise ValueError    # Should be a string at this point
        else:
            ins_index = 1 if self.patient_insurance[0] > 0 else 0
            amount_contacts = None
            chance = random.randint(1, 100)
            for i in buy_contacts:
                amount = buy_contacts[i][int(self.patient_auto[1])][ins_index]
                if chance > amount:
                    chance -= amount
                else:
                    try:
                        amount_contacts = int(contacts_amount[i][contact_type])
                    except TypeError:
                        print(contacts_amount[i])
                    break
            if amount_contacts is not None:
                for i in self.product_list:
                    if contact_type == i[1]:
                        contact_type = i[0]     # Change to id number for quick sale
                self.purchases += [contact_type] * amount_contacts

    def purchase_glasses(self):
        purchase_chance = buy_glasses[int(self.patient_auto[1])][self.patient_insurance[0]]  # Initial value
        bottom, top = random_glasses[int(self.patient_auto[1])]
        purchase_chance += random.randint(bottom, top)
        if self.patient_history:
            frames = {10, 11, 12}
            last_purchase = self.patient_history[self.patient_history_dates[-1]]
            purchased_before = bool(frames.intersection(last_purchase))
            if not purchased_before:
                if self.patient_insurance[0] > 0:
                    purchase_chance += skip_glasses[int(self.patient_auto[1])][1]
                else:
                    purchase_chance += skip_glasses[int(self.patient_auto[1])][0]
        if self.patient_auto[2] != 'Glasses':
            purchase_chance += non_glasses
        purchase_count = 0
        while purchase_chance > 0:
            purchase = random.randint(1, 100)
            if purchase < purchase_chance:
                purchase_count += 1  # Purchased glasses
            purchase_chance -= glasses_threshold
        return purchase_count

    def glasses_type(self, count):  # Puts together all the items on the glasses
        master_purchases = []
        for x in range(count):
            purchase_list = []
            purchase_list.append(self.product_id(self.pick_frame()))
            purchase_list.append(self.product_id(self.pick_lens_type()))
            purchase_list.append(self.product_id(self.pick_lens_material()))
            ar_purchased = self.pick_ar_type()
            if ar_purchased and ar_purchased != 'None':
                purchase_list.append(self.product_id(ar_purchased))
            if x == 1:      # Second pair
                polar_purchased = self.pick_polarized(multi=True)
            else:
                polar_purchased = self.pick_polarized()
            if polar_purchased:
                purchase_list.append(polar_purchased)
            if 25 not in purchase_list:
                trans_purchase = self.pick_transitions()
                if trans_purchase:
                    purchase_list.append(trans_purchase)
            master_purchases += purchase_list
        return master_purchases

    def pick_frame(self):
        chance = random.randint(1, 100) + frame_gender if self.patient_demographics[3] == 'female' else 0
        for i in frame_type:
            if chance > frame_type[i][int(self.patient_auto[1])][self.patient_insurance[0]]:
                chance -= frame_type[i][int(self.patient_auto[1])][self.patient_insurance[0]]
            else:
                return i  # String of frame

    def pick_lens_type(self):   # Choose SV, BF, Prog
        if self.patient_demographics[2] < 40:
            return 'SV Lenses'
        else:
            pass
            patient_lens = None
            if self.patient_history:
                lenses = {13, 14, 15, 16, 17}
                count = 0
                for i in reversed(self.patient_history_dates):
                    if patient_lens is None:
                        patient_lens = lenses.intersection(self.patient_history[i])
                        pass
                    else:
                        if patient_lens == lenses.intersection(self.patient_history[i]):
                            count += 1
                            if count >= 3:
                                break
                        else:
                            chance = random.randint(1, 100)
                            if chance > switch_lens_type - (count * 5):
                                break
                            else:
                                patient_lens = None   # Jump to lens selection
            if patient_lens is None or len(patient_lens) == 0:
                chance = random.randint(1, 100)
                for i in lens_type:
                    if chance > lens_type[i]:
                        chance -= lens_type[i]
                    else:
                        if i == 'Progressives':
                            chance = random.randint(1, 100)
                            for x in progressive_type:
                                if chance > progressive_type[x][int(self.patient_auto[1])][self.patient_insurance[0]]:
                                    chance -= progressive_type[x][int(self.patient_auto[1])][self.patient_insurance[0]]
                                else:
                                    i = x
                                    return i
                        return i    # Returned as string, will have a separate function to change to id.
            return self.product_id(list(patient_lens)[0], to_id=False)

    def pick_lens_material(self):
        if self.patient_demographics[2] < 40:
            return 'Polycarbonate'
        else:
            chance = random.randint(1, 100)
            lenses = None
            if self.patient_history:
                types = {20: "Hi-Index", 19: "Polycarbonate", 18: "Plastic"}
                lens_types = {18, 19, 20}
                for i in reversed(self.patient_history_dates):
                    lenses = lens_types.intersection(self.patient_history[i])
                    if len(lenses) > 1:
                        lenses = types[list(lenses)[0]]
                        break
                    else:
                        lenses = None
            chance += lens_insurance[self.patient_insurance[0]] + lens_buy_pattern[int(self.patient_auto[1])]
            try:
                rx = lens_rx[self.patient_auto[6]]
            except IndexError:  # Outside the high end of the Rx index
                rx = lens_rx[-1]
            chance += rx
            for i in lens_material:
                if lenses == i:
                    chance += loyal_lens_material
                if chance >= lens_material[i]:
                    return i
            return "Plastic"    # 'Else' choice

    def pick_ar_type(self):
        chance = random.randint(1, 50)
        chance += ar_insurance[self.patient_insurance[0]] + ar_buy_pattern[int(self.patient_auto[1])]
        ar = None
        if self.patient_history:
            types = {21: 'Standard AR', 22: 'Good AR', 23: 'Great AR'}
            ar_types = {21, 22, 23}
            for i in reversed(self.patient_history_dates):
                ar = ar_types.intersection(self.patient_history[i])
                if ar:
                    ar = list(ar)[0]
                    ar = types[ar]
                    break
        for i in ar_type:
            if i == ar:
                chance += 20
            if chance >= ar_type[i]:
                return i
        return None

    def pick_transitions(self):
        chance = random.randint(1, 50) + trans_age if self.patient_demographics[2] < 20 else 0
        chance += trans_insurance[self.patient_insurance[0]] + trans_buy_pattern[int(self.patient_auto[1])]
        if self.patient_history and len(self.patient_history) > 1:
            count = 0
            had_it = None
            glasses = {10, 11, 12}
            for i in reversed(self.patient_history_dates):
                purchased = glasses.intersection(self.patient_history[i])
                if purchased:  # Did they buy glasses last time?
                    if had_it is None:
                        if 24 in purchased:
                            had_it = True
                        elif 25 in purchased:       # Polarized doesn't count
                            pass
                        else:
                            count += 1
                    elif count == 1:
                        if 24 in purchased:
                            chance = 0 - trans_loyal  # Did not buy it after having it, must hate it.
                            break
                        elif 25 in purchased:
                            pass
                        else:
                            count += 1
                    elif had_it:
                        if 24 in purchased:
                            chance = 0 + trans_loyal  # Bought it twice in a row, must like it
                            break
                        elif 25 in purchased:
                            pass
                        else:
                            break
        if chance > trans_buy:
            return 24   # Purchased transitions

    def pick_polarized(self, multi=False):
        chance = random.randint(1, 50)
        chance += polar_insurance[self.patient_insurance[0]] + polar_buy_pattern[int(self.patient_auto[1])]
        if multi:
            second_pair = 0 + second_pair_sun
        else:
            second_pair = 0 - (second_pair_sun * 2)
        if self.patient_history and not multi:
            for i in reversed(self.patient_history_dates):
                glasses = {10, 11, 12}
                purchased = glasses.intersection(self.patient_history[i])
                if purchased:
                    if 25 not in self.patient_history[i]:
                        second_pair = 0 + second_pair_sun   # Did not purchase sun last time.
                        break
        if chance + second_pair > polar_buy:
            return 25

    def product_id(self, product, to_id=True):      # Turns str to id or id to str
        if to_id:
            if type(product) == str:
                for i in self.product_list:
                    if product in i:
                        return i[0]
        if not to_id:
            if type(product) == int:
                for i in self.product_list:
                    if product in i:
                        return i[1]

# db = DBCommands()
# patient = 102
# i = db.view_free(f"SELECT sale_item.product_id, sale.purchase_time FROM sale_item INNER JOIN "
#                  f"sale ON sale_item.sale_id = sale.id WHERE sale.patient = {patient}")


# pl = ProductPurchase(102)
# pl.pull_patient_history()
# pl.pull_patient_auto()
# pl.pull_patient_demographics()
# pl.pull_product_list()
#
# print(pl.patient_history, pl.patient_auto, pl.patient_demographics)

"""
*** Logic Dictionaries ***
"""

# Optimap purchase chance. Roll 1 - 50, 30 or more purchase.
optimap = {5: 25, 4: 20, 3: 0, 2: -10, 1: -20}
loyal_optimap = 20  # Added or subtracted per optimap previously purchased.

# Once cl type chosen, will stay until 40 and will roll until special fitting. (Multifocal fit)
cl_exam_type = 70  # Sphere fit, over this is special fitting. (Toric or multifocal)
cl_age_factor = 20       # Subtracted from exam_type starting at 40 and every 10 years after.

# Index of insurances
insurance = ['None', 'Poor', 'Standard', 'Good']

# Determine if a patient will purchase glasses:
# {buying_pattern: [% chance to buy glasses w/o ins, % chance w/ poor ins, % w/ standard ins, % w/ good ins]}
# Over 70% could mean multiple glasses.

buy_glasses = {5: [120, 120, 130, 140], 4: [90, 110, 120, 130],
               3: [40, 60, 70, 80], 2: [20, 50, 60, 70], 1: [0, 30, 40, 50]}

glasses_threshold = 70

# If they did not purchase last year
skip_glasses = {5: [20, 20], 4: [20, 20], 3: [40, 30], 2: [40, 30], 1: [20, 20]}

# Random chance added to either purchase none, or purchase multiple pairs
random_glasses = {5: [-20, 50], 4: [-10, 20], 3: [-20, 30], 2: [-20, 30], 1: [-20, 30]}

# If they are a contact lens or health patient, the reduced chance of buying glasses
non_glasses = -40

# Type of contacts, dailies, bi-weekly, monthly
type_contacts = {"Daily Contacts": {5: 90, 4: 80, 3: 40, 2: 20, 1: 5},
                 "Bi-Weekly Contacts": {5: 5, 4: 10, 3: 30, 2: 30, 1: 35},
                 "Monthly Contacts": {5: 5, 4: 10, 3: 30, 2: 50, 1: 60}}

# Chance to switch contacts once they picked one, decreases by 5% each year until 0 if they don't switch.
# [yearly drop, initial chance]
switch_contacts = [-5, 15]

# How many contacts will they buy? - Insurance type does not change chance.
# If under 100%, remainder will not buy from store. (Online, Costco, etc.)
# "Three Month" section means "One box per eye", so monthly contacts will be the same either way.
buy_contacts = {"Year": {5: [98, 98], 4: [95, 95], 3: [50, 70], 2: [30, 50], 1: [10, 10]},
                "Half Year": {5: [0, 0], 4: [0, 0], 3: [25, 15], 2: [30, 30], 1: [10, 10]},
                "Three Month": {5: [0, 0], 4: [0, 0], 3: [10, 5], 2: [10, 10], 1: [30, 30]}}

# How many boxes
contacts_amount = {"Year": {"Daily Contacts": 8, "Bi-Weekly Contacts": 8, "Monthly Contacts": 4},
                   "Half Year": {"Daily Contacts": 4, "Bi-Weekly Contacts": 4, "Monthly Contacts": 2},
                   "Three Month": {"Daily Contacts": 2, "Bi-Weekly Contacts": 2, "Monthly Contacts": 2}}

# Every time option is picked, patient is more likely to pick same option.
# TODO Figure out how to work this out, solid number increase? % Growth?
loyal_customer = 10

# Glasses options : *** LINKED TO ID OF PRODUCTS IN DB

# Frames purchase
frame_type = {"Fancy Frame": {5: [60, 60, 65, 70], 4: [50, 50, 55, 60], 3: [30, 30, 35, 40],
                              2: [5, 10, 10, 10], 1: [2, 5, 5, 5]},
              "Normal Frame": {5: [35, 37, 33, 29], 4: [30, 40, 40, 45], 3: [40, 40, 40, 40],
                               2: [40, 40, 43, 46], 1: [40, 45, 47, 50]},
              "Basic Frame": {5: [5, 3, 2, 1], 4: [20, 10, 5, 5], 3: [30, 30, 25, 20],
                              2: [55, 50, 47, 44], 1: [58, 50, 48, 45]}}

frame_gender = -10  # If female, add chance to 'Fancy Frame' and to 'Normal Frame' (More likely to buy for style)

# Lens Type - First: Under 40 will buy SV Lenses, over 40 will have a chance to buy other types.
# Index: [SV Lenses, BF Lenses, some type of progressive lenses]
lens_type = {'SV Lenses': 30, 'BF Lenses': 20, 'Progressives': 50}
# Chance to 're-roll' lens type, due to non adapt. Could switch back. (Being convinced to try again or different type)
switch_lens_type = 15   # Decreases by 5% each year until 0 if they don't switch.

progressive_type = {"Best Progressive Lenses": {5: [80, 80, 90, 100], 4: [70, 70, 80, 90], 3: [40, 40, 50, 60],
                                                2: [30, 40, 50, 60], 1: [10, 20, 30, 40]},
                    "Good Progressive Lenses": {5: [15, 15, 5, 0], 4: [25, 25, 15, 5], 3: [40, 40, 30, 20],
                                                2: [20, 20, 20, 20], 1: [10, 20, 30, 40]},
                    "Standard Progressive Lenses": {5: [5, 5, 5, 0], 4: [5, 5, 5, 5], 3: [20, 20, 20, 20],
                                                    2: [50, 40, 30, 20], 1: [80, 60, 40, 20]}}

# Material type, dependent on age. 18 Under must take poly for safety. Over 18 based on buying pattern and RX Str
lens_insurance = [0, 5, 15, 30]  # Based on insurance, adds to better material chance.
lens_rx = [-30, -10, 0, 5, 10, 20, 30, 40]  # Based on Rx, from 0 to 7+, adds a modifier to higher material.
lens_buy_pattern = [0, -20, -10, 0, 10, 20]
# Roll 1 - 50, if number exceeds the material number, they will purchase that material. (Poly most common)
lens_material = {"Hi-Index": 100, "Polycarbonate": 30, "Plastic": -50}  # Plastic is 'else' choice.
# Once they pick a material, they are more likely to stick with that material.
loyal_lens_material = 20  # Minus from chosen, added to others

# Anti-Reflective type
ar_insurance = [0, 20, 30, 40]
ar_buy_pattern = [0, -30, -10, 0, 30, 50]
# Roll 1 - 50.
ar_type = {"Great AR": 80, "Good AR": 40, "Standard AR": 10, "None": 0}  # None is 'else' choice.
loyal_ar_type = 20

# Transitions lens add on.
trans_insurance = [0, 0, 20, 40]  # Usually free on higher insurances
trans_age = 15  # Usually popular to kids under 20
trans_buy_pattern = [0, -40, -30, 0, 10, 20]
trans_buy = 55  # Roll 1 - 50, exceed this number to buy.
trans_loyal = 50  # If they like it, they love it. Have to buy twice in a row to activate. If not, it is a penalty.

# Polarized / Sunglasses.
polar_insurance = [0, 0, 20, 40]
polar_buy_pattern = [0, -50, -30, -10, 0, 10]
second_pair_sun = 30  # Bonus if they have bought a non sun pair type this year or last time. Penalty otherwise.
polar_buy = 40  # Roll 1 - 50, exceed to buy



