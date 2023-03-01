// load the things we need
var express = require('express');
var app = express();
const bodyParser = require('body-parser');

// required module to make calls to a REST API
const axios = require('axios');

var selectedID = "";
app.use(bodyParser.urlencoded());

// set the view engine to ejs
app.set('view engine', 'ejs');



// connecting to mysql
var mysql = require('mysql');
var conn = mysql.createConnection({
    host: 'cis3368.cyt7hdbg5yfy.us-east-2.rds.amazonaws.com',
    user: 'admin',
    password: '12slipperySnake*',
    database: 'CIS3368db'
});

conn.connect(function(err) {
  if (err) throw err;
  console.log('Database is connected successfully !');
});
module.exports = conn;


// use res.render to load up an ejs view file
// index page 
app.get('/', function (req, res) {
    res.render('pages/index')
});

app.post('/processdynamicform', function (req, res) {
    //check argument from form
    console.log(req.body);
    hero = req.body;
    // assign hero to superhero name
    heroname = hero["superhero"];
    hero_tagline = "Superhero aliases: " + heroname

    //superhero API CALL
    axios.get('https://superheroapi.com/api/10221405381743383/search/' + heroname)
        .then((response) => {
            hero_data = response.data["results"]

            hero_info = []
            for (x in hero_data) {
                const obj = hero_data[x]
                let bio = obj.biography
                let image = obj.image
                hero_info.push({
                    name: bio["aliases"],
                    img: image["url"]
                });
            }
            console.log(hero_info)

            res.render('pages/index', {
                hero_info: hero_info,
                hero_tagline: hero_tagline
            });
        });
});



// about page
app.get('/trip', function (req, res) {

    //local API call to my Python REST API that delivers trips
    axios.get('http://127.0.0.1:5000/api/trip')
        .then((response) => {

            var trips = response.data;
            var tagline = "Here is the data coming from my own API";
            console.log(trips);
            // use res.render to load up an ejs view file
            res.render('pages/trip', {
                trips: trips,
                tagline: tagline
            });
        });


});


// destination trips

app.get('/destination', function (req, res) {

    //local API call to my Python REST API that delivers destinations
    axios.get('http://127.0.0.1:5000/api/destination/all')
        .then((response) => {

            var destinations = response.data;
            var tagline1 = "Here is the data coming from my own API";
            console.log(destinations);
            // use res.render to load up an ejs view file
            res.render('pages/destination', {
                destinations: destinations,
                tagline1: tagline1
            });
        });


});


app.get('/plan_trip', function(req, res) {
   var examplevar = "Javascript"
    // use res.render to load up an ejs view file
    res.render("pages/plan_trip.ejs", { examplevar: examplevar});
});


// setup page to add new trip
app.post('/plan_trip', async function (req, res) {
    var tripname = req.body.tripname;
    var destinationid = req.body.destinationid;
    var transportation = req.body.transportation;
    var startdate = req.body.startdate;
    var enddate = req.body.enddate
        
    // add trip to the database
    await axios.post('http://127.0.0.1:5000/api/trip', {
        tripname: tripname,
        destinationid: destinationid,
        transportation: transportation,
        startdate: startdate,
        enddate: enddate,
    })
        .then(function (response) {
            console.log(response.data);
            addtrip = response.data;
        })
    // Passing data to the webpage page
    res.render('pages/plan_trip.ejs', {addtrip: addtrip});
});



app.get('/add_destination', function (req, res) {
    var examplevar = "Javascript"
    // use res.render to load up an ejs view file
    res.render("pages/add_destination.ejs", { examplevar: examplevar });
});


// setup page to add new destination
app.post('/add_destination', async function (req, res) {
    var country = req.body.country;
    var city = req.body.city;
    var sightseeing = req.body.sightseeing
   

    // add destination to the database
    await axios.post('http://127.0.0.1:5000/api/destination', {
        country: country,
        city: city,
        sightseeing: sightseeing
    })
        .then(function (response) {
            console.log(response.data);
            adddest = response.data;
        })
    // Passing data to the webpage page
    res.render('pages/add_destination.ejs', { adddest: adddest });
});






// delete trip page
app.get('/cancel_trip', async function (req, res, next) {
    // output list of all trips to choose from
    await axios.get('http://127.0.0.1:5000/api/trip')
        .then((response) => {
            trips = response.data;
            if (response.data)
                console.log("Home - Delete Trips")
        });
    // Passing data to the webpage page
    res.render('pages/cancel_trip.ejs', { trips: trips });
});


// referred to 'https://codingstatus.com/how-to-delete-data-using-node-js-and-mysql/' for this portion:
app.get('/cancel_trip/:id', function (req, res, next) {
    var id = req.params.id;
    var sql = 'DELETE FROM trip WHERE id = ?';
    db.query(sql, [id], function (err, data) {
        
    });
    res.redirect('/');

});


// Creat update trip page
app.patch('/update_trip', async function (req, res) {
    var id = req.body.id;
    var tripname = req.body.tripname;
    var destinationid = req.body.destinationid;
    var transportation = req.body.transportation;
    var startdate = req.body.startdate;
    var enddate = req.body.enddate

    // update trip to the database
    await axios.post('http://127.0.0.1:5000/api/trip', {
        id: id,
        tripname: tripname,
        destinationid: destinationid,
        transportation: transportation,
        startdate: startdate,
        enddate: enddate
    })
        .then(function (response) {
            console.log(response.data);
            uptrip = response.data;
        })
    // Passing data to the webpage page
    res.render('pages/update_trip.ejs', { uptrip: uptrip });
});


// Creat update trip page
app.patch('/update_destination', async function (req, res) {
    var id = req.body.id;
    var country = req.body.country;
    var city = req.body.city;
    var sightseeing = req.body.sightseeing;


    // update trip to the database
    await axios.post('http://127.0.0.1:5000/api/destination/all', {
        id: id,
        country: country,
        city: city,
        sightseeing: sightseeing,
    })
        .then(function (response) {
            console.log(response.data);
            updest = response.data;
        })
    // Passing data to the webpage page
    res.render('pages/update_destination.ejs', { updest: updest });
});



// delete destination page
app.get('/remove_destination', async function (req, res) {
    // output list of all destination to choose from
    await axios.get('http://127.0.0.1:5000/api/destination/all')
        .then((response) => {
            destinations = response.data;
            if (response.data)
                console.log("Home - Remove Destinations")
        });
    // Passing data to the webpage page
    res.render('pages/remove_destination.ejs', { destinations: destinations });
});


// login page
app.get('/login', function (req, res) {
    var exampleVar = "Javascript";

    // this will render our new login spage
    res.render("pages/login.ejs", { exampleVar: exampleVar });
});

app.post('/process_form', function (req, res) {
    // create a variable to hold the username parsed from the request body
    var username = req.body.username
    // create a variable to hold ....
    var password = req.body.password

    let check = 0;

    if (req.body.rememberme == 'on')
        check = 1;

    console.log("username: " + username);
    console.log("password is: " + password);
    console.log("checkedbox checked: " + check);

    res.render('pages/thanks.ejs', { body: req.body })

})


app.listen(8080);
console.log('8080 is the magic port');

// fertig