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
		f"/api/v1.0/tobs"
		f"<h2>Dynamic routes</h2>"
		f"/api/v1.0/START<br/>"
		f"/api/v1.0/START/END<br/>"
	)

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

#########################################################
# Run App
#########################################################
if __name__ == "__main__":
	app.run(debug=True)