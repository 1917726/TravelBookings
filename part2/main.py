import datetime
import time
import flask
import hashlib
from flask import jsonify
from flask import request
from sql import create_connection
from sql import execute_query
from sql import execute_read_query


app = flask.Flask(__name__)
app.config["DEBUG"] = True


# password 'password' hashed
masterPassword = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
masterUsername = 'username'
validTokens = {"100", "200", "300", "400"}


# 'password' as plaintext should not be used to verify authorization to access. the password should be hashed and the hash should be compared to the stored password hash in the database
@app.route('/authenticatedroute', methods=['GET'])
def auth():
    if request.authorization:
        encoded = request.authorization.password.encode() #unicode encoding
        hashedResult = hashlib.sha256(encoded) #hashing
        if request.authorization.username == masterUsername and hashedResult.hexdigest() == masterPassword:
            return '<h1> WE ARE ALLOWED TO BE HERE </h1>'
    return make_response('COULD NOT VERIFY!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})



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



# view all the destinations: http://127.0.0.1:5000/api/destination/all
@app.route('/api/destination/all', methods=['GET'])
def api_destall():
    return jsonify(destinations)


# view all the trips: http://127.0.0.1:5000/api/trip/all
@app.route('/api/trip', methods=['GET'])
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
def add_trip():
    request_data = request.get_json()
    tripname = request_data['tripname']
    destinationid = request_data['destinationid']
    newtransportation = request_data['transportation']
    newstartdate = request_data['startdate']
    newenddate = request_data['enddate']
    for i in range(len(destinations) - 1, -1, -1):
        if destinations[i]['id'] == destinationid:
            atrip = "INSERT INTO trip(tripname, destinationid, transportation, startdate, enddate) VALUES ('%s','%s','%s','%s','%s')" % (tripname,destinationid, newtransportation, newstartdate, newenddate)
            execute_query(conn, atrip)
            return 'Add request successful'


@app.route('/api/destination', methods=['POST'])  # add destination as POST: http://127.0.0.1:5000/api/destination
def add_destination():
    request_data = request.get_json()

    newcountry = request_data['country']
    newcity = request_data['city']
    newsightseeing = request_data['sightseeing']
    adest = "INSERT INTO destination(country, city, sightseeing) VALUES ('%s','%s','%s')" % ( newcountry, newcity, newsightseeing)
    execute_query(conn, adest)
    return 'Add request successful'

# Update/edit a destination
@app.route('/api/destination', methods=['PATCH'])
def update_dest():
    request_data = request.get_json()
    # request id of destination to update
    destupdate = request_data['id']
    # information that will be replacing the old information associated with the destination ID
    country = request_data['country']
    city = request_data['city']
    sightseeing = request_data['sightseeing']
    for i in range(len(destination) -1,-1,-1):
        if destination[i]['id'] == destupdate:
            update = """
            UPDATE destination
            SET country = '%s', city = '%s', sightseeing = '%s' 
            WHERE id = '%s'"""% (country, city, sightseeing, destupdate)
            execute_query(conn, update)

    return "Destination was updated successfully"


# Update/edit a trip plan
@app.route('/api/trip', methods=['PATCH'])
def update_trip():
    request_data = request.get_json()
    #get the id of the  trip to update
    tripupdate = request_data['id']
    tripname = request_data['tripname']
    destid = request_data['destinationid']
    trans = request_data['transportation']
    sdate = request_data['startdate']
    edate = request_data['enddate']
    for i in range(len(trips) -1,-1,-1):
        if trips[i]['id'] == tripupdate:
            update = """
            UPDATE trip
            SET tripname = '%s', destinationid = '%s', transportation = '%s', startdate = '%s', enddate = '%s' 
            WHERE id = '%s'"""% (tripname,destid, trans, sdate, edate, tripupdate)
            execute_query(conn, update)

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

# delete destination
@app.route('/api/destination', methods=['DELETE'])
def delete_dest():
    request_data = request.get_json()
    destToDelete = request_data['id']
    for i in range(len(destinations) - 1, -1, -1):
        if destinations[i]['id'] == destToDelete:
            del (destinations[i])
    delete_dest = "DELETE FROM destination where id='%s'" % destToDelete
    execute_query(conn, delete_dest)

    return "delete request successful"







app.run()


# Referenced the examples that professor Otto Dobretsberger demonstrated in class

