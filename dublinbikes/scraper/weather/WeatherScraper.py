import requests
import json
from datetime import datetime

from dublinbikes.common.Config import Config
from dublinbikes.scraper.base.WebScraper import WebScraper


class Weather:
    def __init__(self, my_dict, i):
        self.dt = my_dict['hourly'][i]['dt']
        self.temp = my_dict['hourly'][i]['temp']
        self.feels_like = my_dict['hourly'][i]['feels_like']
        self.humidity = my_dict['hourly'][i]['humidity']
        self.clouds = my_dict['hourly'][i]['clouds']
        self.wind_speed = my_dict['hourly'][i]['wind_speed']
        self.visibility = my_dict['hourly'][i]['visibility']
        self.rain = my_dict['minutely'][i]['precipitation']


class WeatherScraper(WebScraper):
    def __init__(self, config):
        WebScraper.__init__(self, config)

    # override parent method: implement feature
    def _request_api(self):
        request = requests.get(
            self._config["APIWLink"] + self._config["APIWKEY"])
        response = request.text
        return response

    # override parent method: implement feature
    def _convert_to_obj(self, response):
        my_dict = json.loads(response)
        # turn it into Weather object
        weather_list = []
        for i in range(0, 24):
            weather_i = Weather(my_dict, i)
            weather_list.append(weather_i)
        return weather_list

    # override parent method: implement feature
    def _create_tables(self):
        # create database
        sql1 = """CREATE DATABASE IF NOT EXISTS dublinbikesdb"""
        self._engine.execute(sql1)

        # create the table for dynamic hourly weather
        sql2 = """CREATE TABLE IF NOT EXISTS hourlyWeather (
                    date_time DATETIME,
                    temp CHAR(10),
                    feels_like CHAR(10),    
                    humidity CHAR(10),
                    clouds CHAR(10),
                    wind_speed CHAR(10),
                    visibility CHAR(10),
                    rain CHAR(10)
                    )"""

        sql_forecast = """CREATE TABLE IF NOT EXISTS hourlyWeatherForecast (
                            date_time DATETIME,
                            temp CHAR(10),
                            feels_like CHAR(10),    
                            humidity CHAR(10),
                            clouds CHAR(10),
                            wind_speed CHAR(10),
                            visibility CHAR(10),
                            rain CHAR(10)
                            )"""

        # create the table for historical hourly weather
        sql3 = """CREATE TABLE IF NOT EXISTS hourlyWeather_hist (
                            id int NOT NULL AUTO_INCREMENT,
                            date_time DATETIME,
                            temp CHAR(10),
                            feels_like CHAR(10),    
                            humidity CHAR(10),
                            clouds CHAR(10),
                            wind_speed CHAR(10),
                            visibility CHAR(10),
                            rain CHAR(10),
                            PRIMARY KEY (id)
                            )"""
        try:
            self._engine.execute(sql2)
            self._engine.execute(sql3)
            self._engine.execute(sql_forecast)
        except Exception as e:
            print(e)

    # override parent method: implement feature
    def _save_to_db(self, weather_list):
        self._hourly_to_db(weather_list[:1])
        self._hourly_forecast_to_db(weather_list[1:])

    # Insert the data into the Database.
    def _hourly_to_db(self, item):
        dt_value = item[0].dt
        epoch_time = int(dt_value)
        time_date = datetime.fromtimestamp(epoch_time)
        datetime_str = time_date.strftime('%Y-%m-%d %H:%M:%S')
        temp = item[0].temp
        feels_temp = item[0].feels_like
        humidity = item[0].humidity
        clouds = item[0].clouds
        wind_speed = item[0].wind_speed
        visibility = item[0].visibility
        rain = item[0].rain
        print("Deleting")
        self._engine.execute("DELETE FROM hourlyWeather")
        print(datetime_str, temp, feels_temp, humidity, clouds, wind_speed,
              visibility, rain)
        vals = (
            datetime_str, temp, feels_temp, humidity, clouds, wind_speed,
            visibility, rain
        )
        self._engine.execute(
            "insert into hourlyWeather values(%s,%s,%s,%s,%s,%s,%s,%s)",
            vals)

        now = datetime.now()
        print("INFO: WeatherScraper._hourly_to_db: now is", now)
        minute = now.minute
        # if the minute is between 30 and 39, then insert history data
        if minute // 10 == 3:
            print("INFO: Start to historical weather data.")
            self._half_hour_to_history(vals)
        return

    # Insert the forecast data into the Database.
    def _hourly_forecast_to_db(self, items):
        print("Deleting hourlyWeatherForecast")
        self._engine.execute("DELETE FROM hourlyWeatherForecast")
        print("Inserting hourlyWeatherForecast")
        for item in items:
            dt_value = item.dt
            epoch_time = int(dt_value)
            time_date = datetime.fromtimestamp(epoch_time)
            datetime_str = time_date.strftime('%Y-%m-%d %H:%M:%S')
            temp = item.temp
            feels_temp = item.feels_like
            humidity = item.humidity
            clouds = item.clouds
            wind_speed = item.wind_speed
            visibility = item.visibility
            rain = item.rain

            print(datetime_str, temp, feels_temp, humidity, clouds, wind_speed,
                  visibility, rain)
            vals = (
                datetime_str, temp, feels_temp, humidity, clouds, wind_speed,
                visibility, rain
            )
            self._engine.execute(
                "insert into hourlyWeatherForecast values(%s,%s,%s,%s,%s,%s,%s,%s)",
                vals)

    def _half_hour_to_history(self, values):
        """Add every 6th row on the half hour to the historical table for
        weather. """
        self._engine.execute("insert into hourlyWeather_hist ("
                             "date_time, temp, feels_like, humidity,"
                             "clouds, wind_speed, visibility, rain)"
                             " values(%s,%s,%s,%s,%s,%s,%s,%s)",
                             values)


if __name__ == "__main__":
    s = WeatherScraper(Config().load())
    s.scrape()
