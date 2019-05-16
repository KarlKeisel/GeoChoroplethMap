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

from flask import Flask, render_template, send_from_directory, request
from flask_sqlalchemy import SQLAlchemy
from password import pg_password
import os

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{pg_password}@localhost/Eyecare'
# Local db url

db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)


class Patients(db.Model):
    __table__ = db.Model.metadata.tables['patients']

    def __repr__(self):
        return self.patient_name, self.address


class Products(db.Model):
    __table__ = db.Model.metadata.tables['products']

    def __repr__(self):
        return self.id, self.product, self.cost


class Sale(db.Model):
    __table__ = db.Model.metadata.tables['sale']


class SaleItem(db.Model):
    __table__ = db.Model.metadata.tables['sale_item']


class Schedule(db.Model):
    __table__ = db.Model.metadata.tables['schedule']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/intro/')
def intro():
    return render_template('intro.html')


@app.route('/geo_map/')
def geo_map():
    return render_template('geo_map.html')


@app.route('/schedule/', methods=['GET', 'POST'])
def schedule():
    if request.method == "POST":
        date = request.form['schedule-date']
        if len(date) > 0:
            patients = db.session.query(Schedule.appt_time, Patients.patient_name, Schedule.appt_type).filter(Schedule.patient == Patients.id).filter_by(appt_date=date).all()
            return render_template('schedule.html', data=patients, schedule_date=date)
        else:
            return render_template('schedule.html', data=False, schedule_date=date)

    return render_template('schedule.html')

# query = db.session.query(table1.col1, table2.col2).filter(table1.col3 == table2.col3)
# print(query.statement)
#
# query2 = db.session.query(table1.col1, table2.col2).join(table2, table1.col3 == table2.col3)
# print(query.statement)
# TODO Make a search list to look at patients based on name, average dollar, latest purchase.


@app.route('/frontend_explained/')
def frontend_explained():
    product = Products.query.order_by(Products.id.desc()).all()
    return render_template('frontend_explained.html', data=product)  # TODO finish this!


@app.route('/backend_explained/')
def backend_explained():
    return render_template('backend_explained.html')


@app.route('/usafavicon.png')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                               'usafavicon.png', mimetype='image/png')


if __name__ == "__main__":
    app.run()
