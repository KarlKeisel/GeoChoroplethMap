import random
from SQL import sales_inserter as si

ii = si.InsertItem()
big_list = random.sample(range(2119), 1000)

# Will be used to quickly populate data into DB, will have to make something more official for the nightly adding.

ii.db._connect()

for person in big_list:     # Works! Can also accept a date as a string '2019/02/14'
    person = str(person)
    errors = []
    try:
        ii.quick_sale(person, None, 'None', [1, 5])
    except IndexError:
        errors.append(person)
    print(", ".split(person) + " had an index error.")


ii.db._commit_close()

# TODO Still need to learn how to code triggers into PostgreSQL using pgplsql language.
# TODO Trigger when patient had a purchase, update 'last_purchase' (Without python code)
# TODO Trigger to calcuate average dollar sale of patient
