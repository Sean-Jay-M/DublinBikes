import pickle
from datetime import datetime

import pandas as pd
from flask import Flask, jsonify, json
from flask import render_template
from flask_cors import CORS, cross_origin

from dublinbikes.common.Config import Config
from dublinbikes.common.DBManager import DBManager
import os

app = Flask(__name__)

# fix the cors issue
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

config = Config()
config_dict = config.load()
model_path = config_dict["MODEL_PATH"]

@app.route("/")
@cross_origin()
def hello():
    return render_template("index.html")
 
@app.route("/stations")
@cross_origin()
def get_stations():
    engine = DBManager(config_dict).engine()
    print(engine)
    data = []
    rows = engine.execute(
        "SELECT * from static;".format())
    for row in rows:
        data.append(dict(row))
    return jsonify(available=data)

@app.route("/stationsCurrent/")
@cross_origin()
def get_station():
    engine = DBManager(config_dict).engine()
    print(engine)
    data = []
    rows = engine.execute(
        "SELECT * FROM dynamicCurrent;".format())
    for row in rows:
        data.append(dict(row))

    return jsonify(available=data)

@app.route("/weatherCurrent/")
@cross_origin()
def get_weather():
    engine = DBManager(config_dict).engine()
    print(engine)
    data = []
    rows = engine.execute(
        "SELECT * FROM hourlyWeather;".format())
    for row in rows:
        data.append(dict(row))

    return jsonify(available=data)

@app.route("/airCurrent/")
@cross_origin()
def get_airquality():
    engine = DBManager(config_dict).engine()
    print(engine)
    data = []
    rows = engine.execute(
        "SELECT * FROM airquality;".format())
    for row in rows:
        data.append(dict(row))

    return jsonify(available=data)

@app.route("/prediction2/")
@cross_origin()
def get_prediction2():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/", "dummy_json.json")
    data = json.load(open(json_url))
    # return render_template('showjson.jade', data=data)
    return jsonify(data)

@app.route("/prediction/<station_number>")
@cross_origin()
def get_prediction(station_number):
    print(f'start prediction for station_number: {station_number}')
    engine = DBManager(config_dict).engine()
    predict_input = {}

    weather_list_dict = {}
    # get the current weather
    current_weather = engine.execute(
        "SELECT * FROM hourlyWeather".format())
    for row in current_weather:
        weather_data = dict(row)
        for key in weather_data:
            weather_list_dict.update({key: [weather_data[key]]})
        # date_time is not required by the model
        del weather_data['date_time']

    # get the forecast weather data
    forecast_weather = engine.execute(
        "SELECT * FROM hourlyWeatherForecast".format())
    for row in forecast_weather:
        weather_data = dict(row)
        for key in weather_data:
            value_list = weather_list_dict[key]
            value_list.append(weather_data[key])
            weather_list_dict.update({key: value_list})
    # date_time is not required by the model
    del weather_list_dict['date_time']

    print(weather_list_dict)
    predict_input.update(weather_list_dict)

    # generate the prediction date times for the model
    current_time = datetime.now()
    hours = []
    days = []
    day_times = []
    for i in range(24):
        future_time = current_time + pd.DateOffset(hours=i+1)
        hour = future_time.hour
        hours.append(hour)
        day = future_time.weekday()
        days.append(day)
        day_times.append(f'{day}{hour}')

    # concatenate all model input features
    predict_input.update({'hour': hours, 'day': days, 'day_time': day_times})
    print(f'Data used for prediction for station {station_number}\n{predict_input}')
    X_test = pd.DataFrame(data=predict_input)
    print(f'Dataframe: \n{X_test}')

    # load the model from disk by station_number
    bikes_model = pickle.load(open(f'{model_path}/bikes/{station_number}', 'rb'))
    bike_stands_model = pickle.load(open(f'{model_path}/bike_stands/{station_number}', 'rb'))
    # predict number of bikes
    # reference: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html
    bikes_prediction = bikes_model.predict(X_test)
    print(f'Prediction result for station {station_number}:\n{bikes_prediction}')
    cap_prediction(bikes_prediction)
    print(f'[After cap]Prediction result for station {station_number}:\n{bikes_prediction}')

    bike_stands_prediction = bike_stands_model.predict(X_test)
    print(f'Prediction result for station {station_number}:\n{bike_stands_prediction}')
    cap_prediction(bike_stands_prediction)
    print(f'[After cap]Prediction result for station {station_number}:\n{bike_stands_prediction}')

    result = format_data(hours, bikes_prediction, bike_stands_prediction)

    return jsonify(result)


# the minimum number of bikes or bike stands is 0
def cap_prediction(prediction):
    for index, value in enumerate(prediction):
        if value < 0:
            prediction[index] = 0
    return prediction


# align the features and put them into a list for convenience of frontend
def format_data(hours, prediction, bike_stands_prediction):
    result_list = []
    for index, hour in enumerate(hours):
        if hour not in [1,2,3,4]:
            data = {'hour': hour,
                    'available_bikes': round(prediction[index]),
                    'available_bike_stands': round(bike_stands_prediction[index])}
            result_list.append(data)
    return result_list


if __name__ == "__main__":
    # set dataframe to let it show all columns
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', -1)

    # the host that flask will be exposed to
    flask_host = config_dict["FLASK_HOST"]
    app.run(debug=True, host=flask_host)
