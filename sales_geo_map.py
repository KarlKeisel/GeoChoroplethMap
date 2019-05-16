"""
Karl's Sales Geo Map Site

This app will take information from a data source, (.csv or eventually a SQL database) and populate it
on a choropleth map. It will focus on geolocation for customer addresses, and use multiple layers to allow
looking at the data from multiple angles.

Functions:
Showing customer addresses on the main map,
Allowing filtering based on age, gender, first year purchased, last year purchased, average dollar amount.

Goals:
I want to be able to take customer data and find patterns in sales. This could allow be targeting on sales and emails,
or show where people may be getting missed if they are no longer purchasing.

Future Plans:
A scheduler that can populate a form to be printed out that shows patients for that day and potential dollar amount.
(Different python file to be connected through HTML)
A way to auto update from data source to find any changes and to update the information.
"""

# Main flask file that holds the front end and connects the back end.

from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/geo_map/')
def geo_map():
    return render_template('geo_map.html')

# TODO Make scheduler page that will display the schedule for patients and prediction model. Updates when requested.
# TODO Make a search list to look at patients based on name, average dollar, latest purchase.




@app.route('/backend_explained/')
def backend_explained():
    return render_template('backend_explained.html')


@app.route('/usafavicon.png')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                               'usafavicon.png', mimetype='image/png')


if __name__ == "__main__":
    app.run(debug=True)
