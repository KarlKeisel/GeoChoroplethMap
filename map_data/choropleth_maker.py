"""
This file will hold all the information for making the choropleth map and making the layers needed to visualize
sales data. It will accept information of multiple types for a patient, filling blanks with NaN values and placing
them onto a choropleth map.

Data Needed:
Name, Address, Geo-Coordinates, Age, Average Dollar Amount.
"""

import folium
import pandas as pd
from SQL.postgresqlcommands import DBCommands


def pull_data():
    db = DBCommands()
    columns = ['ID', 'Name', 'Address', 'Ins', 'Average Dollar', 'Age', 'Gender', 'Latitude', 'Longitude',
               'First Purchase', 'Last Purchase']
    data = db.view_free('SELECT * FROM patients WHERE avg_dollar IS NOT NULL')
    df = pd.DataFrame(data, columns=columns)
    return df


# TODO Map maker seems busted, fix!!!
def create_map(data):

    name = list(data['Name'])
    address = list(data['Address'])
    # Insurance
    avg_dol = list(data['Average Dollar'])
    age = list(data['Age'])
    gender = list(data['Gender'])
    lat = list(data['Latitude'])
    lon = list(data['Longitude'])
    # First Purchase
    # Last Purchase

    # Name. <br> Age, Gender. <br> Average Dollar.
    html = """<strong> %s </strong> <br>
    %s, %s <br>
    $ %s
    """

    def gender_color(gen):  # For use in color coding for a gender layer.
        if gen == 'Male':
            return 'blue'
        else:
            return 'pink'

    def gender_icon(gen):  # For use in icon display of gender.
        if gen == 'Male':
            return 'glyphicon-king'
        else:
            return 'glyphicon-queen'

    def average_dollar(money):  # Blue to Yellow to Orange; Using tags instead of heat mapping
        if int(money) < 200:
            return '#4286f4'  # Deep blue
        elif int(money) < 350:
            return '#3fb8f4'  # Blue
        elif int(money) < 500:
            return '#3ef2ce'  # Teal
        elif int(money) < 650:
            return '#3ef16d'  # Green
        elif int(money) < 800:
            return '#dfe238'  # Yellow
        else:
            return '#e2a338'  # Orange

    web_map = folium.Map(location=[34.026165, -84.3277459], no_wrap=True, zoom_start=12)

    fg1 = folium.FeatureGroup(name="Average Dollar")  # Color people by average dollar.
    for lt, ln, nm, sex, ag, dol in zip(lat, lon, name, gender, age, avg_dol):
        try:
            iframe = folium.IFrame(html=html % (nm, ag, sex, dol), width=200, height=100)
            fg1.add_child(folium.CircleMarker(location=(lt, ln), popup=folium.Popup(iframe), color=average_dollar(dol),
                                              fill=True, fill_opacity=0.8, radius=6))
        except ValueError:  # If Lat or Long is a nan value
            pass

    web_map.add_child(fg1)
    web_map.add_child(folium.LayerControl())

    web_map.save("../templates/geo_map.html")


create_map(pull_data())
