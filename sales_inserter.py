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

    def _id_lookup(self, table, column, item):  # Returns id of item
        id_key = None
        try:
            id_key = self.db.view(table, conditional=(column, item), field="id")
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

        sale_id = self._id_lookup('sale', 'purchase_time', sale_time)  # Grab sales id for sale_item table

        for item in items:  # Creating sale_item table
            self.db.insert(['sale_item', ('product_id', item[0]), ('sale_id', sale_id), ('price', item[1])])

        # TODO Work on updating datetime on last purchase
        # self.db.update_timestamp(patient, sale_time)

    def quick_sale(self, patient_id, time, insurance, item_ids):    # Used for quickly inputting sales for testing
        items = []
        for item_id in item_ids:
            items.append(self.db.view('products', field="product, cost", conditional=("id", item_id))[0])
        patient = self.db.view('patients', field="patient_name", conditional=("id", patient_id))[0][0]
        print(patient, time, insurance, items)
        self.insert_sale(patient, time, insurance, items)

    def sales_viewer(self, patient, time=None, ):
        pass
    # TODO Way to look up and print out sales during a certain date?


class Observer(object):  # Will keep record of any changes so nightly updates are far faster.
    pass
