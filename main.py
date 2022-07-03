import datetime
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref
# from sqlalchemy.sql.expression import func
import os

app = Flask(__name__)

##Connect to Database
flight_db = 'sqlite:///flight.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flight.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
apikey= "TopSecretAPIKey"

class Aircraft(db.Model):
    __tablename__ = "aircrafts"
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.String(250), unique=True, nullable=False)
    manufacturer = db.Column(db.String(250), nullable=False)
    aircraft_serial_num = relationship("Flight", back_populates="serial")

## TABLE Configuration
class Flight(db.Model):
    __tablename__ = "flights"
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Key, "aircrafts.id" the aircrafts refers to the tablename of aircrafts.
    aircraft_id = db.Column(db.Integer, db.ForeignKey("aircrafts.id"))
    # reference to the Aircraft object, the "serial" refers to the serial property in the Aircraft class.
    serial = relationship("Aircraft", back_populates="aircraft_serial_num")

    departure_airport = db.Column(db.String(250), nullable=False)
    arrival_airport = db.Column(db.String(250), nullable=False)

    # SQLite, date and time types are stored as strings which are then converted back to datetime objects when rows are returned
    departure_date = db.Column(db.String(250), nullable=False)
    arrival_date = db.Column(db.String(250), nullable=False)

    # def make_dict(self):
    #     dictionary = {}
    #     for values in self.__table__.columns:
    #         dictionary[values.name] = getattr(self, values.name)
    #     return dictionary

    def make_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

if not os.path.isfile(flight_db):
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/all", methods= ['GET','POST'])
def get_all_flights():
    all_flights = db.session.query(Flight).all()
    flight_list = []
    for flights in all_flights:
        flight_list.append(flights.make_dict())
    information = jsonify(flight=flight_list)
    return information
    # single line version
    # return jsonify(flight_list=[flight.make_dict() for flight in all_flights])

@app.route("/search", methods= ['GET','POST'])
def search_flight_dep():
    departure_airport =request.args.get('dep')
    departure_selected = Flight.query.filter_by(departure_airport=departure_airport).all()
    arrival_airport =request.args.get('arr')
    arrival_selected = Flight.query.filter_by(arrival_airport=arrival_airport).all()

    dep_flights_selected = []
    for flights in departure_selected:
        dep_flights_selected.append(flights.make_dict())

    arr_flights_selected = []
    for flights in arrival_selected:
        arr_flights_selected.append(flights.make_dict())

    if dep_flights_selected:
        return jsonify(flight=dep_flights_selected)
    elif arr_flights_selected:
        return jsonify(flight=arr_flights_selected)
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a flight at that departure or arrival location."})

@app.route("/searchdate", methods= ['GET','POST'])
def search_flight_date():
    #data format : departure_date_start and departure_date_end must be: "%m/%d/%Y,%H:%M"
    departure_date_start =request.args.get('starttime')
    departure_date_end = request.args.get('endtime')
    now = datetime.datetime.now().strftime("%m/%d/%Y,%H:%M")
    if departure_date_start > now:
        date_selected = db.session.query(Flight).filter(Flight.departure_date.between(departure_date_start, departure_date_end)).all()
        flights_selected = []
        for flights in date_selected:
            flights_selected.append(flights.make_dict())
        if flights_selected:
            return jsonify(flight=flights_selected)
        else:
            return jsonify(error={"Not Found": "Sorry, we don't have a flight at that time range."})
    else:
        return jsonify(error={"Wrong Date Range": "Sorry, you can only search flights for future departures."})

@app.route("/addflight", methods= ['GET','POST'])
def add_flight():
    now = datetime.datetime.now().strftime("%m/%d/%Y,%H:%M")
    departure_airport= request.form.get('departure_airport')
    arrival_airport= request.form.get('arrival_airport')
    departure_date = request.form.get('departure_date')
    arrival_date = request.form.get('arrival_date')
    aircraft_id = request.form.get('aircraft_id')
    if departure_date < now:
        return jsonify(response={"fail": "A flight can only be created for a future departure"})

    else:
        aircraft_check = Aircraft.query.filter_by(id=aircraft_id).first()
        if aircraft_check:
            add_new_flight = Flight(departure_airport=departure_airport, arrival_airport= arrival_airport, departure_date=departure_date, arrival_date=arrival_date, aircraft_id=aircraft_id)
            print(add_new_flight)
            db.session.add(add_new_flight)
            db.session.commit()
            return jsonify(response={"success": "Successfully added the new flight."})
        else:
            add_new_flight = Flight(departure_airport=departure_airport, arrival_airport= arrival_airport, departure_date=departure_date, arrival_date=arrival_date)
            print(add_new_flight)
            db.session.add(add_new_flight)
            db.session.commit()
            return jsonify(response={"Info": "Aircraft is not listed in the database.Successfully added the new flight without aircraft info."})

@app.route('/patch/<int:flight_id>', methods= ['GET','PATCH'])
def update_aircraft(flight_id):
    update_aircraft_info = Flight.query.get(flight_id)

    if update_aircraft_info:
        aircraft_check = request.args.get('aircraft_serial')
        update_aircraft_check = Aircraft.query.filter_by(serial=aircraft_check).first()
        if update_aircraft_check:
            update_aircraft_info.aircraft_id = update_aircraft_check.id
            db.session.commit()
            return jsonify(response={"success": "Successfully updated flight; aircraft serial data."})
        else:
            return jsonify(response={"fail": "No aircraft with this serial."})

    else:
        return jsonify(response={"fail": "No flight with this id."})

@app.route('/report-closed/<int:flight_id>',methods= ['GET','DELETE'])
def delete_flight(flight_id):
    api_check = request.args.get("api-key")
    if api_check == apikey:
        delete_flight = Flight.query.get(flight_id)
        if delete_flight:
            db.session.delete(delete_flight)
            db.session.commit()
            return jsonify(response={"success": "Successfully delete the flight"})
        else:
            return jsonify(response= {"error": {"Not Found": "Sorry flight with that id was not found in the database."}})
    else:
        return jsonify(response={"error": "Sorry, that's not allowed. Make sure you have the correct api_key."})

if __name__ == '__main__':
    app.run(debug=True)
