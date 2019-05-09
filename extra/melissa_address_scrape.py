"""
Karl's Web Scraper for the Melissa Data Website

Using the carrier routes tab, will pull all the addresses and for any city and rural routes.

Usage:
Enter zip codes into the zipcodes list, then it will cycle through and pull all addresses and put them into a CSV File.
"""

# TODO Work on logging into website.

import requests
from bs4 import BeautifulSoup
import pandas

zipcodes = ['30009', '30022', '30076', '30075', '30076', '30350']  # Roswell zipcodes

address_list_complete = []

for codes in zipcodes:
    r = requests.get(f"https://www.melissa.com/v2/lookups/cartzip/zipcode?zipcode={codes}")
    c = r.content

    soup = BeautifulSoup(c, "html.parser")

    carts = []

    table = soup.find("table", {"id": "tableOne"})

    print(f"Looking up carts for {codes}")
    table_row = table.find_all("tr")
    for x in range(1, len(table_row)):
        cart = table_row[x].find("td").text
        if 'C' in cart or 'R' in cart:
            carts.append(cart.strip())

    for cart in carts:
        r = requests.get(f"https://www.melissa.com/v2/lookups/cartzip/zipcode/{codes}/{cart}")
        c = r.content

        soup = BeautifulSoup(c, "html.parser")

        address_list = []

        table = soup.find("table", {"id": "tableZip4List"})

        table_row = table.find_all("tr")
        for x in range(1, len(table_row)):
            line = table_row[1].find_all("td")
            grouping = []
            for i in line[:2]:
                if i.text:
                    grouping.append(i.text.strip())
            address_list.append(grouping)

        def address_count(start, end, street, scale, zipcode, single=False):
            global address_list_complete
            if single:
                address_list_complete.append(f"{start} {street} Roswell, GA {zipcode}")
            else:
                starter = int(start)
                length = int((int(end) - int(start)) / scale)
                for step in range(length):
                    address_list_complete.append(f"{starter} {street} Roswell, GA {zipcode}")
                    starter += scale

        def address_maker(address, zipcode):
            scale = 1
            single = False
            if '(' in address[0]:
                scale = 2
            numbers = address[0].split(' ')
            if len(numbers) > 1:
                start = numbers[0]
                end = numbers[2]
            else:
                single = True
            address_count(start, end, address[1], scale, zipcode, single)
        
        for address in address_list:
            address_maker(address, codes)

    df = pandas.DataFrame()
    df['Address'] = pandas.DataFrame(data=address_list_complete)
    df.to_csv(f"Address_List_Zip_{codes}.csv", index=False)
