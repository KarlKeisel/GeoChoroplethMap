"""
Takes patients from schedule, and if they have purchased before will return predicted buying pattern,
or "New" if never bought before.

Using previously calibrated decision tree.
"""

from joblib import load
import pandas as pd
from SQL.postgresqlcommands import DBCommands
from statistics import mode, StatisticsError
from datetime import date


class DTree(object):

    def __init__(self, work_day, path):
        self.work_day = work_day
        self.dtree = load(filename='./machine_learning/glasses_dtree.joblib')
        self.db = DBCommands()
        self.db.connect()

    def __del__(self):
        self.db.conn.close()

    def pull_patient_id(self):
        patient_list = []
        patients = self.db.view_free(
            f"SELECT patient FROM schedule WHERE appt_date = '{self.work_day}' ORDER BY appt_time", slow=False)
        for patient in patients:
            patient_list.append(patient[0])  # Patients in order of appointment times
        return patient_list

    def pull_patient_data(self, patient):
        data = self.db.view_free(f"SELECT * FROM glasses_data WHERE id = {patient}", slow=False)
        return data

    def process_data(self, data):
        if len(data) == 0:
            return 'New'
        else:
            columns = ['id', 'patient_name', 'address', 'insurance', 'avg_dollar', 'age', 'gender', 'lat', 'lon',
                       'first_purchase', 'last_purchase', 'purchase_time', 'total_paid', 'used_ins', 'product_id',
                       'price', 'appt_type', 'buying_pattern']  # Getting column titles ready
            df = pd.DataFrame(data, columns=columns)
            df.drop_duplicates(inplace=True)
            df.drop(columns=['address', 'first_purchase', 'last_purchase', 'patient_name', 'purchase_time', 'id', 'lat',
                             'lon', 'buying_pattern'], axis=1, inplace=True)  # Cleaning data

            # Getting categorical data, including missing columns then dropping first.
            gender = pd.get_dummies(df['gender']).reindex(columns=['female', 'male'], fill_value=0)
            exam_type = pd.get_dummies(df['appt_type']).reindex(columns=['Contacts', 'Glasses', 'Health'],
                                                                fill_value=0)
            insurance = pd.get_dummies(df['insurance']).reindex(columns=['Good', 'Standard', 'Poor', 'None'],
                                                                fill_value=0)
            gender.drop(columns=['female'], axis=1, inplace=True)
            exam_type.drop(columns=['Contacts'], axis=1, inplace=True)
            insurance.drop(columns=['Good'], axis=1, inplace=True)
            df.drop(columns=['gender', 'appt_type', 'insurance', 'used_ins'], axis=1, inplace=True)

            df2 = pd.concat([df, gender, exam_type, insurance], join='inner', axis=1)

            predictions = self.dtree.predict(df2)
            try:
                return mode(predictions)
            except StatisticsError:
                return predictions[0]

    def predict_pattern(self):
        pattern_list = []
        for i in self.pull_patient_id():
            pattern_list.append(self.process_data(self.pull_patient_data(i)))
        return pattern_list
