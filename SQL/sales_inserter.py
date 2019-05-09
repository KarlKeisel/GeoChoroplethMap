"""
Used to insert sales or new patients into the system.
Will also create a file that will let the cron_updater.py know what has changed.
"""

# TODO Create an observer that will create a change log for the day.

import datetime as dt
from SQL.postgresqlcommands import DBCommands


# TODO Create a way to verify patient isn't a duplicate. (Name and age equal current person)

class InsertItem(object):   # This would connect to the front end to allow DB editing
    def __init__(self):
        self.db = DBCommands()

    def _id_lookup(self, table, column, item, slow=True):  # Returns id of item
        id_key = None
        try:
            id_key = self.db.view(table, conditional=(column, item), field="id", slow=slow)
        except Exception:
            self.db.rollback()
        if id_key is None:
            print(f'DB Error, could not find id of {item}')
        else:
            return id_key[0][0]  # Should never be none: Cannot sale to unknown, nor sale unknown item.

    def patient_insert(self, name, address='', gender='', age='', insurance='None'):  # Needs a name
        try:
            self.db.insert(['patient', ('patient_name', name), ('address', address), ('gender', gender),
                            ('age', age), ('insurance', insurance)])
        except Exception:   # Look at exceptions that could hinder insert.
            self.db.rollback()

    def insert_sale(self, patient, time=None, insurance='None', purchase_items=(('Test', 0))):
        # Slow and terrible, quick_sale will be the main input function.
        # Expects a nested list with [item, price] as each item.
        total_sum = 0
        sale_time = time if time else dt.datetime.now()  # Insert current time if none supplied
        patient_id = self._id_lookup('patients', 'patient_name', patient)
        items = []
        for item in purchase_items:
            item_id = self._id_lookup('products', 'product', item[0])
            total_sum += int(item[1])
            items.append([item_id, item[1]])    # Change item name to item id
        # Create sale (patient, purchase_time, total_paid, used_ins)
        self.db.insert(['sale', ('patient', patient_id), ('purchase_time', sale_time),
                        ('total_paid', total_sum), ('used_ins', insurance)])

        sale_id = self.db.view(f"sale WHERE purchase_time = '{sale_time}' AND patient = {patient_id}", field="id")

        for item in items:  # Creating sale_item table
            self.db.insert(['sale_item', ('product_id', item[0]), ('sale_id', sale_id[0][0]), ('price', item[1])])

        self.db.update_avg_dollar(patient_id)
        self.db.update_timestamp(patient, sale_time)
        print(f"Patient {patient} recorded.")

    def quick_sale(self, patient_id, time, insurance, item_ids):    # Used for quickly inputting sales for testing
        total_sum = 0
        sale_time = time if time else dt.datetime.now()  # Insert current time if none supplied
        items = []

        for item_id in item_ids:
            items.append(self.db.view('products', field="id, cost", conditional=("id", item_id), slow=False)[0])
            total_sum += int(items[0][1])

        self.db.insert(['sale', ('patient', patient_id), ('purchase_time', sale_time),
                        ('total_paid', total_sum), ('used_ins', insurance)], slow=False)

        sale_id = self.db.view(f"sale WHERE purchase_time = '{sale_time}' AND patient = {patient_id}",
                             field="id", slow=False)

        for item in items:  # Creating sale_item table
            self.db.insert(['sale_item', ('product_id', item[0]), ('sale_id', sale_id[0][0]),
                            ('price', item[1])], slow=False)

        self.db.update_avg_dollar(patient_id,slow=False)
        self.db.update_timestamp(patient_id, sale_time, slow=False)
        # print(f"Patient {patient_id} recorded.")


class Observer(object):  # Will keep record of any changes so nightly updates are far faster.
    pass
