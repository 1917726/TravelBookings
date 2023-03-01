import datetime
import time
import flask
from flask import jsonify
from flask import request
from sql import create_connection
from sql import execute_query
from sql import execute_read_query


app = flask.Flask(__name__)
app.config["DEBUG"] = True


conn = create_connection('cis3368.cyt7hdbg5yfy.us-east-2.rds.amazonaws.com', 'admin', '12slipperySnake*', 'CIS3368db')
select_destination = "SELECT * FROM destination"
destination = execute_read_query(conn, select_destination)

# create table for destinations
create_destination_table = """
create table if not exists destination(
id int auto_increment,
country varchar(30) not null,
city varchar(30) not null,
sightseeing varchar(200) not null,
primary key (id)
"""
dest = "SELECT * FROM destination"
destinations = execute_read_query(conn, dest)
result = []


### Example of putting in destinations into detination table
#newdestinations = """
#insert destination(country, city, sightseeing)
#values ("USA", "Houston", "Nothing"),
#("Mexico", "Mexico City", "Pyramids"),
#("Egypt", "Cairo", "Giza Pyramids"),
#("Hungary", "Budapest", "Danube river")
#"""



#create table for trips + info
create_trip_table = """
create table if not exists trip(
id int auto_increment,
destinationid int not null,
transportation varchar(30) not null,
startdate date not null,
enddate date not null,
primary key (id),
foreign key (destinationid) references destination(id)
)"""


trip = "select * from trip"
trips = execute_read_query(conn, trip)
results = []



# default url
@app.route('/', methods=['GET'])
def home():
    return "<h1> WELCOME TO OUR FIRST API! </h1>"

# view all the trips: http://127.0.0.1:5000/api/trip/all
@app.route('/api/trip/all', methods=['GET'])
def api_all():
    return jsonify(trips)

# finding a unique trip by id: http://127.0.0.1:5000/api/trip?id=1
@app.route('/api/trip', methods=['GET'])
def api_id():
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return 'ERROR: No ID provided!'

    results = []
    for trip in trips:
        if trip['id'] == id:
            results.append(trip)
    return jsonify(results)


@app.route('/api/trip', methods=['POST'])  # add trip as POST: http://127.0.0.1:5000/api/trip
def add_example():
    request_data = request.get_json()
    destinationid = request_data['destinationid']
    newtransportation = request_data['transportation']
    newstartdate = request_data['startdate']
    newenddate = request_data['enddate']
    for i in range(len(destination) - 1, -1, -1):
        if destination[i]['id'] == destinationid:
            atrip = "INSERT INTO trip(destinationid, transportation, startdate, enddate) VALUES ('%s','%s','%s','%s')" % (destinationid, newtransportation, newstartdate, newenddate)
            execute_query(conn, atrip)
    return 'Add request auccessful'

# Update/edit a trip plan
@app.route('/api/trip', methods=['PATCH'])
def update_trip():
    request_data = request.get_json()
    tripupdate = request_data['id']
    destid = request_data['destinationid']
    trans = request_data['transportation']
    sdate = request_data['startdate']
    edate = request_data['enddate']
    for i in range(len(trips) -1,-1,-1):
        if trips[i]['id'] == tripupdate:
            update = """
            UPDATE trip
            SET destinationid = '%s', transportation = '%s', startdate = '%s', enddate = '%s' 
            WHERE id = '%s'"""% (destid, trans, sdate, edate, tripupdate)
            execute_query(conn, update)
        else:
            return 'No valid trip under that id'
    return "Trip was updated successfully"




# delete trip
@app.route('/api/trip', methods=['DELETE']) 
def delete_trip():
    request_data = request.get_json()
    tripToDelete = request_data['id']
    for i in range(len(trips) - 1, -1, -1):
        if trips[i]['id'] == tripToDelete:
            del (trips[i])
    delete_trip = "DELETE FROM trip where id='%s'" % tripToDelete
    execute_query(conn, delete_trip)

    return "delete request successful"


@app.route('/api/trip', methods=['GET'])
def api_trips_id():
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return 'ERROR: No ID provided!'

    conn = create_connection('your connection details here')
    sql = "SELECT * FROM trips"
    trips = execute_read_query(conn, sql)
    results = []

    for trip in trips:
        if trip['id'] == id:
            results.append(trip)
    return jsonify(results)

# display the destination(s) and their sightseeing options
@app.route('/api/destination', methods=['GET'])
def api_destination():
    conn = create_connection('cis3368.cyt7hdbg5yfy.us-east-2.rds.amazonaws.com', 'admin', '12slipperySnake*','CIS3368db')
    sql = "SELECT * FROM destination"
    logs = execute_read_query(conn, sql)
    return jsonify(logs)


app.run()


# Referenced the examples that professor Otto Dobretsberger demonstrated in class
