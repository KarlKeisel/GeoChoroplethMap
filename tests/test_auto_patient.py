from automatic.auto_patient import *
from SQL.postgresqlcommands import DBCommands
from collections import Counter
from datetime import datetime, timedelta, date, time
import pytest

# pytest -v -p no:warnings

db = DBCommands()
# np = NewPatient(2)
#
#
# patients = np.patient_selector()
#
#
# db.connect()
#
# auto_pat = db.view('auto_patient', slow=False)
# print(auto_pat)
#
# # products = db.view('products', slow=False)
# # print(products)
#
#
# db.conn.rollback()
# db.conn.close()

#
# exam = []
# for i in range(500):
#     exam.append(plogic.create_exam_type(70))
#
# Counter(exam)
# print(Counter(exam))

exam_date = date(2014, 2, 20)
print(Scheduler)