"""
This file will hold all the information for making the choropleth map and making the layers needed to visualize
sales data. It will accept information of multiple types for a patient, filling blanks with NaN values and placing
them onto a choropleth map.

Data Needed:
Name, Address, Geo-Coordinates, Age, Average Dollar Amount.
"""

import folium
import pandas as pd


def create_map(file="sample_data.csv"):

    data = pd.read_csv(file)   # Pull out data

    lat = list(data['Latitude'])
    lon = list(data['Longitude'])
    name = list(data['Name'])
    address = list(data['Address'])
    gender = list(data['Gender'])
    age = list(data['Age'])
    avg_dol = list(data['Average Dollar'])

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

    def gender_icon(gen):   # For use in icon display of gender.
        if gen == 'Male':
            return 'glyphicon-king'
        else:
            return 'glyphicon-queen'

    def average_dollar(money):  # Blue to Yellow to Orange; Using tags instead of heat mapping
        if int(money) < 100:
            return '#4286f4'    # Deep blue
        elif int(money) < 200:
            return '#3fb8f4'    # Blue
        elif int(money) < 300:
            return '#3ef2ce'    # Teal
        elif int(money) < 400:
            return '#3ef16d'    # Green
        elif int(money) < 500:
            return '#dfe238'    # Yellow
        else:
            return '#e2a338'    # Orange

    web_map = folium.Map(location=[34.026165, -84.3277459], no_wrap=True, zoom_start=12)

    fg1 = folium.FeatureGroup(name="Average Dollar")    # Color people by average dollar.
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
