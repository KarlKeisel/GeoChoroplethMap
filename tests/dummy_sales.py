import random
import sales_inserter as si

ii = si.InsertItem()
big_list = random.sample(range(2119), 1000)

ii.db._connect()

for person in big_list:
    person = str(person)
    try:
        ii.quick_sale(person, None, 'None', [1, 5])
    except IndexError:
        print(f"{person} had an index error.")


ii.db._commit_close()

