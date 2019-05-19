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
from sqlalchemy import and_
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
            patients = db.session.query(Schedule.appt_time, Patients.patient_name, Schedule.appt_type).filter(
                Schedule.patient == Patients.id).filter_by(appt_date=date).all()
            return render_template('schedule.html', data=patients, schedule_date=date)
        else:
            return render_template('schedule.html', data=False, schedule_date=date)
    # TODO Fix horizontal bar on schedule loading.
    return render_template('schedule.html', data='First')


@app.route('/patient_search/', methods=['GET', 'POST'])
def patient_search():
    if request.method == "POST":
        patient = request.form['patient-name']
        avg_top = request.form['avg-top']
        avg_bot = request.form['avg-bot']
        avg_top, avg_bot = float(avg_top) * 100, float(avg_bot) * 100
        patients = Patients.query.filter(and_(Patients.avg_dollar >= avg_bot, Patients.avg_dollar <= avg_top)).filter(
            Patients.patient_name.like(f'%{patient}%'))
        patients_count = patients.count()
        return render_template('patient_search.html', patients=patients, patient=patient, avg_bot=avg_bot,
                               avg_top=avg_top, patients_count=patients_count)
    patients = Patients.query.all()
    return render_template('patient_search.html', patients=patients, patients_count=1)


@app.route('/patient_search/<patient>/')
def patient_history(patient):
    patient = patient.split('%20')
    patient = str(' '.join(patient))  # Removing the whitespace between first and last name.
    patient_info = Patients.query.filter_by(patient_name=patient).first()
    sale_history = Sale.query.filter_by(patient=patient_info.id)
    sale_count = sale_history.count()
    return render_template('patient_history.html', patient=patient, patient_info=patient_info,
                           sale_history=sale_history, sale_count=sale_count)


@app.route('/patient_search/<patient>/<sale_id>/')
def sale_list(patient, sale_id):
    sale_id = sale_id
    sale = Sale.query.filter_by(id=sale_id).first()
    item_list = db.session.query(Products.product, SaleItem.price).filter(Products.id == SaleItem.product_id).filter(
        SaleItem.sale_id == sale_id).all()
    return render_template('sale_list.html', patient=patient, item_list=item_list, sale=sale)


@app.route('/datamap_explained/')
def datamap_explained():
    return render_template('datamap_explained.html')


@app.route('/frontend_explained/')
def frontend_explained():
    return render_template('frontend_explained.html')


@app.route('/backend_explained/')
def backend_explained():
    return render_template('backend_explained.html')


@app.route('/master.css')
def css():
    return send_from_directory(os.path.join(app.root_path, 'static', 'css'), 'master.css')


@app.route('/usafavicon.png')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                               'usafavicon.png', mimetype='image/png')


if __name__ == "__main__":
    app.run()
