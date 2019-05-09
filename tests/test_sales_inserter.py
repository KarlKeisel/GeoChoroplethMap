"""
Testing sales_inserter plus the DB Commands (Which is imported into sales_inserter
"""

from SQL import sales_inserter as si
from datetime import date

ii = si.InsertItem()
# print('Asserting if _id_lookup correctly returns an id.')
# assert ii._id_lookup('patients', 'patient_name', 'Angeles Pollard') == 1332
# ii.db.connect()
# ii.quick_sale("1500", None, 'VSP', [1, 5, 6])
# ii.db.commit_close()
# ii.insert_sale('Newton Powers', purchase_items=[('Eye Exam', 8500), ('Refraction', 4900)])  # Works!

# ii.db.delete('sale', ('patient', 1332))

# ii.db.update(['products', ('id', 1), ('id', 29)])

#
# sales_items = ii.db.view('sale_item')
# print(sales_items)

# patient = ii.db.view('patients', ('patient_name', 'Angeles Pollard'))
# print(patient)

# print(ii.db.view('sale', ('purchase_time::date', '2019-02-23')))
#
# ii.db._connect()
# for i in range(2100):
#     ii.db.update_avg_dollar(i, slow=False)    # Works!
#
# ii.db._commit_close()

if __name__ == '__main__':
    products = ii.db.view('products')
    for item in products:
        print(f"({item[0]}) {item[1]} -  ${(item[2] / 100)}")

    sales = ii.db.view('sale')
    print(sales)

    sale_time = date(2014, 2, 20)
    patient_id = 102
    sale_id = ii.db.view(f"sale WHERE purchase_time = '{sale_time}' AND patient = {patient_id}", field="id")
    print(sale_id)

