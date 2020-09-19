from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import datetime as dt


# create engine
engine = create_engine('sqlite:///hawaii.sqlite', connect_args={'check_same_thread': False})
Base = automap_base()
Base.prepare(engine, reflect = True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)


# step 1:
app = Flask(__name__)
@app.route("/")
def paths():
    # urls that tell the user the end points that are available
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start date<br/>"
        f"/api/v1.0/start date/end date"
    )

@app.route("/precipitation")
def precipitation():
    lastDayinDB = dt.date(2017, 8, 23)
    OneYearAgo = lastDayinDB - dt.timedelta(days = 365)
    last_year = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= OneYearAgo).all()
    last = {}
    for x,y in last_year:
        last[x]=y
    return jsonify(last)

@app.route("/stations")
def stations():
    # return a list of all of the stations in JSON format
    station_list = session.query(Station.station).all()
    stationOneD = list(np.ravel(station_list))
    return jsonify(stationOneD)


@app.route("/tobs")
def tobs():
    lastDayforStation = dt.date(2017, 8, 18)
    OneYearAgoforStation = lastDayforStation - dt.timedelta(days = 365)
    year_temp = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= OneYearAgoforStation).\
        filter(Measurement.station == 'USC00519281').all()
    temps = {}
    for x,y in year_temp:
        temps[x]=y
    return jsonify(temps)

# Return a JSON list of the minimum temperature, the average temperature, 
# and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for 
# all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, 
# and TMAX for dates between the start and end date inclusive.

@app.route("/<start_date>")
def start(start_date):
    start_temp = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    start_temp_ravel = list(np.ravel(start_temp))
    return jsonify(start_temp_ravel)

@app.route("/<start_date>/<end_date>")
def end(start_date,end_date):
    start_and_end = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    start_and_end_ravel = list(np.ravel(start_and_end))
    return jsonify(start_and_end_ravel)

#2nd step:
if __name__ == '__main__':
    app.run()