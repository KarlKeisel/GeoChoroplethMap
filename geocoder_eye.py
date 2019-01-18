"""
Used to create geo locations specific to the sales_geo_map app.

Will be used first with full addresses, then fine tuned for the eventual SQL DB that it will use to make geo locations.

Future Plans:
Will be able to, or have another program to pull the data and input into the map app.
"""

import pandas as pd
from geopy.geocoders import ArcGIS
from geopy.exc import GeocoderTimedOut
from time import sleep


class GeocoderAdd(object):

    def __init__(self, file):
        self.file = file            # Unopened CSV File given
        self.database = None        # Initial database
        self.geocoded = None        # Eventual return database

    def _check_database(self):      # Checks if db has a column labelled 'address' or 'Address'
        try:
            self.database = pd.read_csv(self.file)
        except Exception:           # Make sure file is a .csv file
            return False
        else:
            if "Address" in self.database.columns or "address" in self.database.columns \
             or "ADDRESS" in self.database.columns:
                return True
            else:
                return False            # DB does not have the correct field, return error

    def transform_database(self):   # Runs geocoding and returns geocoded database
        if self._check_database():
            df = self.database
            arc = ArcGIS()

            def geo_pause(x):       # Recursive to help deal with time out errors
                try:
                    y = arc.geocode(x, timeout=10)
                    print('Applying geo coords to ' + str(x))
                except GeocoderTimedOut:
                    print('Error on ' + str(x) + ', retrying.')
                    geo_pause(x)
                else:
                    sleep(1)  # Pause per geopy policy
                    return y

            try:
                df["Coordinates"] = df["Address"].apply(geo_pause)
            except KeyError:
                return False
            # TODO Add an exception handle for 'timeout' errors that will try again later.
            else:
                df["Latitude"] = df["Coordinates"].apply(lambda x: x.latitude if x != None else None)
                df["Longitude"] = df["Coordinates"].apply(lambda x: x.longitude if x != None else None)
                self.geocoded = df


if __name__ == '__main__':
    pass

