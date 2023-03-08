import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite") #create engine to call to sqlite database

# reflect an existing database into a new model
Base = automap_base() #creates internal copy/object of database

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement 
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__) #create class called name


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""

    return (
        f"Welcome! This is a Flask API designed to provide climate information.<br/>"
        f"<br/>"
        f"Please see below list of Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"For the below route, which searches data using dates, please enter start and end dates in the following formats:<br/>" 
        f"For search with only start date: /api/v1.0/temps/MM-DD-YYYY <br/>"
        f"For search with start and end dates: /api/v1.0/temps/MM-DD-YYYY/MM-DD-YYYY <br/>"
        f"<br/>"
        f"<Route: br/>"
        f"/api/v1.0/temps/<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    #create session
    # session = Session(engine)

    """Return the precipitation data for the last year"""
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    
    session.close()

    # Create dictionary with date as the key and prcp as the value
    precipitation_data = []
    for date, prcp in precipitation:
        precipitation_dict = {}
        precipitation_dict ["date"] = date
        precipitation_dict ["precipitation"]= prcp
        precipitation_data.append(precipitation_dict)

    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():

    """Return a list of stations."""
    #query for list of stations
    results = session.query(Station.station).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    stations = list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
 
    """Return the temperature observations (tobs) for previous year."""
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the primary station for all tobs from the last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))

    # Return the results
    return jsonify(temps=temps)


@app.route("/api/v1.0/temps/<start>")
@app.route("/api/v1.0/temps/<start>/<end>")

def stats(start=None, end=None): 

    """Return TMIN, TAVG, TMAX."""
    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end: #if user does not provide end date
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()

        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)

    
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == '__main__':
    app.run(debug=True)
