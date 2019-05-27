"""
Will create and process fake data to help test main app.

Roswell Ga Area: 34.121930, -84.395609 ; 33.968075, -84.273057

Future Plans:
Need to generate sales per patient. Will probably have to use SQL or a DB for that.
"""

from mimesis import Person
from mimesis.enums import Gender
import random
import numpy as np
import pandas as pd
from map_data import geocoder_eye as geo

""" This will hold functions for quickly generating random info to help populate a table.

name: Will quickly generate english 'en' names through mimesis. If gender is needed, add True and will populate a
tuple with (name, gender), otherwise will just return a string. (Number of names needed, gender=False)

number: Using numpy, will generate a bell curve of numbers centered around a mean. Returned as integer.
(Number needed, Mean (default = 40), [bot, top age] (default = [5, 70])
Used for ages, and average dollar amounts.
"""


def random_name(number, gender=False):          # Used for name and gender
    people = []  # Returned with names and if needed, genders
    per = Person('en')
    for i in range(number):
        if gender:  # If gender is important
            choice = random.randint(0, 1)
            if choice == 1:
                people.append((per.full_name(gender=Gender.MALE), 'male'))     # Save as tuple
            else:
                people.append((per.full_name(gender=Gender.FEMALE), 'female'))
        else:
            people.append(per.full_name())
    return people       # Return list


def random_number(number, mean=40, scale=50, edges=(5, 70)):      # Used for age and average dollar
    nums = []   # Returned with ints of values
    for i in range(number):
        num = np.random.normal(loc=mean, scale=scale)    # Generate the number
        while num < edges[0] or num > edges[1]: # Check to make sure it is within the top and bot margins.
            num = np.random.normal(loc=mean, scale=scale)  # Regenerate the number
        nums.append(int(num))
    return nums


if __name__ == '__main__':
    # print(random_name(5, True))   # Test cases
    # print(random_name(5))
    # print(random_number(5))
    # print(random_number(5, 300, 200, (40, 2000)))

    # main_df = pd.DataFrame(columns=['Address'])
    # for i in range(9):  # Pulls the addresses from multiple csv files and takes 7% into 1.
    #     df = pd.read_csv('sample_data/Address_List_Test' + str(i) + '.csv')
    #     df.rename(columns={'0': 'Address'}, inplace=True)   # Were not originally named 'Address'
    #     df = df.sample(frac=0.15)
    #     main_df = pd.concat([df, main_df], sort=False)
    #
    # num_address = len(main_df)        # Gets the length of address
    # people_gender = random_name(num_address, True)  # Generate names
    # people = []     # Store names
    # gender = []     # Store gender
    # age = random_number(num_address)    # Generate Ages
    # for i in people_gender:
    #     people.append(i[0])
    #     gender.append(i[1])
    # main_df['Name'] = people
    # main_df['Gender'] = gender
    # main_df['Age'] = age
    # print(main_df.head())
    # main_df.to_csv('test_list.csv', index=False)

    # df = pd.read_csv('test_list.csv')       # Dropping duplicate addresses (That should already not be there)
    # df.drop_duplicates(subset='Address', inplace=True)
    # df.to_csv('sample_data_2.csv')

    # loc = geo.GeocoderAdd('sample_data_2.csv')            # Needs the unopened csv file
    # loc.transform_database()                            # Adds the new geo columns
    # df = loc.geocoded                                   # Grabs the new files
    # df.drop(columns=['Coordinates'], inplace=True)
    # df.to_csv('sample_data_2.csv', index=False)

    # df = pd.read_csv('sample_data_2.csv')
    # df.drop(columns=['Unnamed: 0'], inplace=True)
    # print(df.info())
    # df.to_csv('sample_data_2.csv', index=False)
    pass

