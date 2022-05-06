let map;
function initMap() {
    //init a google map
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 14,
        center: new google.maps.LatLng(53.34511048273914, -6.267027506499677),
        mapTypeId: "terrain",
    });
    //set map to 45 degree satellite view
    map.setTilt(45);
    //add a bike layer which shows bike paths
    const bikeLayer = new google.maps.BicyclingLayer();
    bikeLayer.setMap(map);
    //add infowindow in map
    console.log("setting infowindows....");
    infowindow = new google.maps.InfoWindow();
    console.log("setting hostname....");
    hostname = "54.158.231.1";

    //show station markers on the map
    function showStationMarkers() {
        // get json and show markers on map
       $.getJSON("http://" + hostname + ":5000/stations", function (data) {
        //load the other data
        $.getJSON("http://" + hostname + ":5000/stationsCurrent/", function (data2) {
        // $.getJSON("http://" + hostname + ":5000/prediction2/", function (data3) {
        //                 var prediction = data3;
                        var stationsLive = data2.available;
                        var stations = data.available;
                        console.log('stations', stations);
                        console.log('stationsLive', stationsLive);

                        //initiate the counter for the stationsLive as stations and stationsLive follow the same order
                        console.log("var integerLive....");
                        var integerLive = 0; //counter for live data

                        //draw markers and add click on events on markers
                        console.log("iterating stations to create markers....");
                        Object.keys(stations).forEach(key => {
                            const station = stations[key];
                            //console.log(station);
                            //console.log("creating marker for...." + station.name);
                            var markers = new google.maps.Marker({
                                position: {
                                    lat: station.position_lat,
                                    lng: station.position_lng,
                                },
                                map: map,
                                details: {
                                    name: station.name,
                                    number: station.number,
                                    bike_stands: station.bike_stands,
                                    banking: (station.banking == 0 ? 'No' : 'Yes'),
                                    status: station.status,
                                    available_bike_stands: stationsLive[integerLive].available_bike_stands,
                                    available_bikes: stationsLive[integerLive].available_bikes,
                                    // prediction: prediction[integerLive].prediction,
                                },
                                label: {
                                    text: "directions_bike",
                                    fontFamily: "Material Icons",
                                    color: "white",
                                    fontSize: "18px",
                                },
                            });
                            //console.log("Marker created for station: " + station.name);
                            //click on event
                            markers.addListener("click", () => {
                                map.setZoom(16); //zoom in
                                map.setCenter(markers.getPosition()); //center to that marker
                                onMarkerClick1(markers); // one option is to call out an info window
                                onMarkerClick2(markers); //another is to replace the content of the side panel
                                document.getElementById("side-panel-body").style.display = "initial"; //open side panel
                                document.getElementById("side-panel-trigger").style.display = "initial"; //show close side panel toggle icon
                                showPrediction(markers.details.number);//replace contents in prediction table
                                createChart(markers.details.number);
                            });
                            integerLive += 1;
                        })
            // })
        })
                .fail(function () {
                    console.log("error");
                })
        })
    }
    showStationMarkers();


    // Info window trigger function
    function onMarkerClick1(markers) {
        // Create content  
        var contentString = markers.details.name + "<br> Station Number: " + markers.details.number + "<br> Total Bike Stands: " + markers.details.bike_stands + "<br> Card Accepted: " + markers.details.banking + "<br> Station Status: " + markers.details.status +
        "<br> Available Stands: " + markers.details.available_bike_stands + "<br> Available Bikes: " + markers.details.available_bikes;

        // Replace our Info Window's content and position 
        infowindow.setContent(contentString);
        infowindow.setPosition(markers.getPosition());
        infowindow.open(map)
    }

    // This function will replace the contents in side panel with different static station data, jquery used
    function onMarkerClick2(markers) {
        // Create content  
        var name = markers.details.name;
        var number = markers.details.number;
        var bike_stands = markers.details.bike_stands;
        var banking = markers.details.banking;
        var status = markers.details.status;
        var available_bike_stands = markers.details.available_bike_stands;
        var available_bikes = markers.details.available_bikes;

        // Replace contents in the side panel
        $(document).ready(function () {
                $("#stationname").text("Station Name: "+ name);
                $("#stationnumber").text("Station Number: "+ number);
                $("#bikestands").text("Bike Stands: "+ bike_stands);
                $("#banking").text("Banking: "+ banking);
                $("#status").text("Open Status: "+ status);
                $("#AvailableBikeStands").text("Available Stands: "+ available_bike_stands);
                $("#AvailableBikes").text("Available Bikes: "+ available_bikes);
        });
    }

    //This function fill the three columns in the prediction table with null data (create a tagged table first)
    function showTimeslots() {
        //fill up the table with three empty columns
        for (var i=0; i<20; i++) {
            $("#table_body").append("<tr>" + "<td id=time_slots" + i + ">time</td>" + "<td id=AB" + i + ">AB</td>" + "<td id=ABS" + i + ">ABS</td>" + "</tr>");
        }
    }
    showTimeslots();

    //this function fill up the table with predictions
    function showPrediction(number) {
        $.getJSON("http://" + hostname + ":5000/prediction/" + number, function (data3) {
            var prediction = data3;
            console.log(prediction);
            var table = document.getElementById("table_body"); //get the table element
            //sort the data by hour ascending, and append the table with its prediction data
            for (var i = 0; i < prediction.length; i++) {
                //append prediction table
                var index_time = "#time_slots"+i;
                $(index_time).text(prediction[i].hour+":00");
                var index_AB = "#AB"+i;
                $(index_AB).text(prediction[i].available_bikes);
                var index_ABS = "#ABS" +i;
                $(index_ABS).text(prediction[i].available_bike_stands);
            };
        })
    }


    //This function is used to display the bar chart
    function createChart(number){
    $.getJSON("http://" + hostname + ":5000/prediction/" + number, function (data4) {
            var predictionGraph = data4;
            console.log(predictionGraph);
            var xValues = [];
            var available_bikes_list = [];
            var available_stands_list = [];

            for (let i = 0; i < predictionGraph.length; i++) {
              xValues.push(predictionGraph[i].hour);
            }

            for (let i = 0; i < predictionGraph.length; i++) {
              available_stands_list.push(predictionGraph[i].available_bike_stands);
            }

            for (let i = 0; i < predictionGraph.length; i++) {
              available_bikes_list.push(predictionGraph[i].available_bikes);
            }

            new Chart("myChart", {
              type: "line",
              data: {
                labels: xValues,
                datasets: [{
                  label: 'Available Bikes',
                  data: available_bikes_list,
                  borderColor: "#5ac5d6",
                  fill: false
                },{
                  label: 'Available Bike Stands',
                  data: available_stands_list,
                  borderColor: "#a05ad6",
                  fill: false
                }]
              },
              options: {
                legend: {display: true},
                hover: {mode: null},
                tooltips: {enabled: false},
                events: [],
              }
            });
        console.log(available_bikes_list);
        console.log(available_stands_list);
        });
    }


    //this function is used to display weather&air_quality data
    function showWeatherAqi() {
        $.getJSON("http://" + hostname + ":5000/weatherCurrent/", function (data4) {
        $.getJSON("http://" + hostname + ":5000/airCurrent/", function (data5) {
           var aqi_all = data5.available[0];
           var weather = data4.available[0];
           var aqi = aqi_all.aqi;
           var temperature = weather.temp;
           var feels_like = weather.feels_like;
           var rain = (weather.rain == 0? 'Sunny':'Rainy');
           var wind_speed = weather.wind_speed;
           console.log("haha:\n" + aqi + "\n" + temperature + "\n" + feels_like + "\n" + rain + "\n" + wind_speed);

       // Replace contents in the side panel
        $(document).ready(function () {
                $("#aqi").text("Air Quality Index: "+ aqi);
                $("#temperature").text("Temperature: "+ temperature + " ℃");
                $("#feels_like").text("Feels Like: "+ feels_like + " ℃");
                $("#rain").text("Weather description: "+ rain);
                $("#wind_speed").text("Wind Speed: "+ wind_speed + " m/s");
        });

       })
       })
    }
    showWeatherAqi();

}
