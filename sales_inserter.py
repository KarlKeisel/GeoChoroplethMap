"""
Used to insert sales or new patients into the system.
Will also create a file that will let the cron_updater.py know what has changed.
"""

# TODO Create a class that will insert sales into system.
# TODO and new patients
# TODO and edit patients
# TODO Create an observer that will create a change log for the day.

import datetime as dt
from SQL.postgresqlcommands import DBCommands


class InsertItem(object):   # This would connect to the front end to allow DB editing
    def __init__(self):
        self.db = DBCommands()

    def patient_insert(self, name, address='', gender='', age='', insurance='None'):  # Needs a name
        try:
            self.db.insert(['patient', ('patient_name', name), ('address', address), ('gender', gender),
                            ('age', age), ('insurance', insurance)])
        except Exception:   # Look at exceptions that could hinder insert.
            print('DB Error')

    def patient_edit(self, table='patient', *args):  # Expects a list with the 'WHERE foo = bar' is the LAST list inside
        pass

    def insert_sale(self, patient_id, time, insurance='None', purchase_items=(('Test', 0))):
        # Expects a nested list with [item, price] as each item.
        pass
