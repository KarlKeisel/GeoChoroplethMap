"""
Testing sales_inserter plus the DB Commands (Which is imported into sales_inserter
"""

import sales_inserter as si

ii = si.InsertItem()
# print('Asserting if _id_lookup correctly returns an id.')
# assert ii._id_lookup('patients', 'patient_name', 'Angeles Pollard') == 1332

products = ii.db.view('products')
for item in products:
    print(f"({item[0]}) {item[1]} -  ${(item[2]/100)}")

# ii.quick_sale("1332", None, 'VSP', [1, 5, 6])

# ii.insert_sale('Angeles Pollard', purchase_items=[('Eye Exam', 8500), ('Refraction', 4900)])  # Works!

# ii.db.delete('sale', ('patient', 1332))

# ii.db.update(['products', ('id', 1), ('id', 29)])


sales = ii.db.view('sale')
print(sales)

sales_items = ii.db.view('sale_item')
print(sales_items)

# patient = ii.db.view('patients', ('patient_name', 'Angeles Pollard'))
# print(patient)


