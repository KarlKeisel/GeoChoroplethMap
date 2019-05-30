# Eyewear Sales Data
Full app that takes data from a database and displays it on a choropleth map and use flask to display a schedule and patient search area.


Hello all!

This is my big dive into something more business focused. It's main function is to take data from a SQL database and populate a website styled interface designed with Flask in order to visualize sales data (From an eye doctor's office).

It's two main functions are to use a choropleth map to visualize where customers live and how much they purchase, and to create a doctor's schedule showing who is being seen that day and use machine learning to predict likely purchases from that patient.

It will then use an updater function to keep the data up to date.

In order to do this first part, I also have constructed apps to create fake data and patients.

I have a jupyter notebook file I use to scrape data from a postal route list, which then used with the library Memesis, creates fake patients. Then run those real addresses through the Geopy library to find lat and lon in order to plot them on the map.

I will then make a final app that will use the same updater to keep creating new patients and purchases in order to make it seem like a living office.

IN ORDER TO RUN:

app.py : The Flask server that will run the whole website. Need to be on and running.

cron_updater.py : The function that will auto update all information at a certain time. (Currently 3 AM each day)

* As of now it needs a copy of the data base, but I have included all the files that will allow you to take the real addresses and populate with fake names and identities.
