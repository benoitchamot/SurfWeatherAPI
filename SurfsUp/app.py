#########################################################
# Dependencies
#########################################################
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import desc
from pathlib import Path

#########################################################
# Functions
#########################################################

def str_to_date(in_string):
# Convert a date stored as a string from the database and convert it to a datetime object.
# Input string format: YYYY-MM-DD
    out_date = dt.datetime.strptime(in_string, '%Y-%m-%d')
    return dt.date(out_date.year, out_date.month, out_date.day)

def last_12_months(date_string):
# Return the most recent date and a date a year ago from the most recent date
# Input: date in string format YYYY-MM-DD
# Output 1: most recent date (datetime)
# Output 2: date a year from the most recent date (datetime)

    # Convert string to datetime
    most_recent_date = str_to_date(date_string)

    # Design a query to retrieve the last 12 months of precipitation data and plot the results.
    # Starting from the most recent data point in the database. Calculate the date one year from the last date in data set.
    most_recent_date_plus_1y = dt.date(most_recent_date.year - 1, most_recent_date.month, most_recent_date.day)

    return most_recent_date, most_recent_date_plus_1y

#########################################################
# Database Setup
#########################################################

# Create engine to hawaii.sqlite
print("Connecting to database...")
db_path = Path('Resources/hawaii.sqlite')
engine = create_engine(f"sqlite:///{db_path}")
print("Connected.")

# Reflect the database into a new model
print("Reflecting database...")
Base = automap_base()
print("Done.")

# Reflect the tables
print("Reflecting tables...")
try:
	Base.prepare(engine, reflect=True)
	print("Done.")
except Exception as inst:
    print(f"\nError: {inst}")
    print("\n*** HINT: please run script from within SurfsUp directory ***\n")
    quit()

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

#########################################################
# Flask Setup
#########################################################
app = Flask(__name__)

#########################################################
# Flask Routes
#########################################################

# Default route
@app.route("/")
def home():
	print("Server received request for Home page")
	return (
		f"<h1>Hawaii Weather API</h1>"
		f"<h2>Static routes</h2>"
		f"/api/v1.0/precipitation<br/>"
		f"<ul>"
		f"	<li>Returns precipitation data for the last 12 months</li>"
		f"	<li>There are multiple data points per day (multiple stations)</li>"
		f"	<li>Key: Date (string, YYYY-MM-DD)</li>"
		f"	<li>Value: Precipitation (in mm)</li>"
		f"</ul>"
		f"/api/v1.0/stations<br/>"
		f"<ul>"
		f"	<li>Returns information for all stations in the database</li>"
		f"	<li>Each station includes: id, name, latitude, longitude and elevation</li>"
		f"</ul>"
		f"/api/v1.0/tobs"
		f"<ul>"
		f"	<li>Returns temperatures for station USC00519281</li>"
		f"	<li>Data are for the last 12 months</li>"
		f"	<li>Each row includes: datetime, temperature in degC</li>"
		f"</ul>"
		f"<h2>Dynamic routes</h2>"
		f"/api/v1.0/&#x003C;start_date&#x003E;<br/>"
		f"<ul>"
		f"	<li>Returns min, max and average temperature for each date</li>"
		f"	<li>Returns value from &#x003C;start_date&#x003E to end of table</li>"
		f"	<li>Date format must be: YYYY-MM-DD</li>"
		f"</ul>"
		f"/api/v1.0/&#x003C;start_date&#x003E/&#x003C;end_date&#x003E;<br/>"
		f"<ul>"
		f"	<li>Returns min, max and average temperature for each date</li>"
		f"	<li>Returns value from &#x003C;start_date&#x003E to &#x003C;end_date&#x003E</li>"
		f"	<li>Date format must be: YYYY-MM-DD</li>"
		f"	<li>&#x003C;end_date&#x003E must be greater or equal to &#x003C;start_date&#x003E</li>"
		f"	<li>All temperatures are in degC</li>"
		f"</ul>"
	)

# Static precipitation route
@app.route("/api/v1.0/precipitation")
def api_precipitation():
	# Open session to the database
	session = Session(bind=engine)

	# Find the most recent date in the dataset
	most_recent_date_string = session.query(measurement).order_by(desc(measurement.date)).first().date
	most_recent_date, most_recent_date_plus_1y = last_12_months(most_recent_date_string)

	# Query the data ordered by date in descending order (most recent to least recent)
	measurement_new_to_old = session.query(measurement).order_by(desc(measurement.date))
	
	# Create empty lists
	precipitation_dicts = []

	# Loop through the measurements
	for row in measurement_new_to_old:
		# Convert date to datetime
		row_date = str_to_date(row.date)
    
    	# If the date is more recent than the limit date (1 year from most recent date)
    	# and the precipitations values are not null...
		if (row_date >= most_recent_date_plus_1y) & (type(row.prcp) == float):
        	# ... then add the data to a dictionary
			prcp_dict = {str(row_date): row.prcp}

			# Append the data to the list of dictionary
			precipitation_dicts.append(prcp_dict)

	# Close session
	session.close()

	# Return jsonified dictionary
	return jsonify(precipitation_dicts)

# Static station route
@app.route("/api/v1.0/stations")
def api_stations():
	# Open session to the database
	session = Session(bind=engine)

	# Query the data from the station table
	stations = session.query(station)

	# Create an empty list
	station_dicts = []

	# Loop through the table rows
	for row in stations:
		# Add data to a dictionary
		station_row = {'id': row.id, 
		 			'station': row.station,
					'name': row.name,
					'latitude': row.latitude,
					'longitude': row.longitude,
					'elevation': row.elevation}
		
		# Add dictionary to list
		station_dicts.append(station_row)

	# Close session
	session.close()

	# Return jsonified dictionary
	return jsonify(station_dicts)

# Static tobs route (for station USC00519281)
@app.route("/api/v1.0/tobs")
def api_tobs():

	# Use most active station:
	most_active_station = 'USC00519281'
	
	# Open session to the database
	session = Session(bind=engine)

	# Using the most active station id
	most_active_station_query = session.query(measurement).filter(measurement.station == most_active_station).order_by(desc(measurement.date))

	# Query the last 12 months of temperature observation data for this station
	station_most_recent_date_string = most_active_station_query.first().date
	station_most_recent_date, station_most_recent_date_plus_1y = last_12_months(station_most_recent_date_string)

	# Create empty lists
	tobs_dicts = []

	# Loop through the measurements
	for row in most_active_station_query:
    	# Convert date to datetime
		row_date = str_to_date(row.date)
    
    	# If the date is more recent than the limit date (1 year from most recent date)
    	# and the precipitations values are not null...
		if (row_date >= station_most_recent_date_plus_1y) & (type(row.tobs) == float):
        	# ... then append the data to a dictionary
			tobs = {'Date': row_date, 'Temperature': row.tobs}
			
			# Add dictionary to list
			tobs_dicts.append(tobs)

	# Close session
	session.close()

	# Return jsonified dictionary
	return jsonify(tobs_dicts)

# Dynamic route (with start date)
@app.route("/api/v1.0/<start_date>")
def api_startdate(start_date):
	
	# Convert date to datetime
	try:
		start_date_dt = str_to_date(start_date)
	except:
		error_message = {'Error': 'Date format not accepted. Make sure date is formatted as YYYY-MM-DD'}
		return jsonify(error_message)

	# Open session to the database
	session = Session(bind=engine)

	# Select columns and perform calculation
	sel = [measurement.date,
    	func.min(measurement.tobs),
    	func.max(measurement.tobs),
    	func.avg(measurement.tobs)]

	# Get the date, and temperature min, max and average, group by date
	temperature_data = session.query(*sel).group_by(measurement.date)

	# Creat an empty list
	temp_data_dicts = []

	# Loop through the data
	for row in temperature_data:
		# Convert date to datetime
		row_date = str_to_date(row.date)
		# Compare the date to the start date
		if (row_date >= start_date_dt):
			# Add data to dictionary
			data_dict = {'Date': row_date, 'TMIN': row[1], 'TMAX': row[2], 'TAVG': row[3]}
			temp_data_dicts.append(data_dict)

	# Close session
	session.close()

	# Return jsonified dictionary
	return jsonify(temp_data_dicts)

# Dynamic route (with start date and end date)
@app.route("/api/v1.0/<start_date>/<end_date>")
def api_startenddates(start_date, end_date):
	
	# Convert start date to datetime
	try:
		start_date_dt = str_to_date(start_date)
	except:
		error_message = {'Error': 'Sart date format not accepted. Make sure date is formatted as YYYY-MM-DD'}
		return jsonify(error_message)
	
	# Convert end date to datetime
	try:
		end_date_dt = str_to_date(end_date)
	except:
		error_message = {'Error': 'End date format not accepted. Make sure date is formatted as YYYY-MM-DD'}
		return jsonify(error_message)
	
	# Check that the start and end date are compatible
	if end_date_dt < start_date_dt:
		error_message = {'Error': 'End date must be greater or equal to start date.'}
		return jsonify(error_message)
	
	# Open session to the database
	session = Session(bind=engine)

	# Select columns and perform calculation
	sel = [measurement.date,
    	func.min(measurement.tobs),
    	func.max(measurement.tobs),
    	func.avg(measurement.tobs)]

	# Get the date, and temperature min, max and average, group by date
	temperature_data = session.query(*sel).group_by(measurement.date)

	# Creat an empty list
	temp_data_dicts = []

	# Loop through the data
	for row in temperature_data:
		# Convert date to datetime
		row_date = str_to_date(row.date)
		# Compare the date to the start and end date
		if (row_date >= start_date_dt) & (row_date <= end_date_dt):
			# Add data to dictionary
			data_dict = {'Date': row_date, 'TMIN': row[1], 'TMAX': row[2], 'TAVG': row[3]}
			temp_data_dicts.append(data_dict)

	# Close session
	session.close()

	# Return jsonified dictionary
	return jsonify(temp_data_dicts)

#########################################################
# Run App
#########################################################
if __name__ == "__main__":
	app.run(debug=True)