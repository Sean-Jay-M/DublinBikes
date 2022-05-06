import requests
import json
import datetime

from dublinbikes.common.Config import Config
from dublinbikes.scraper.base.WebScraper import WebScraper


class AirQuality:
    def __init__(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])


class AirQualityScraper(WebScraper):
    def __init__(self, config):
        WebScraper.__init__(self, config)

    # override parent method: implement feature
    def _request_api(self):
        try:
            request = requests.get(
                self._config["AIRQUALITY_API"] + self._config["AIRQUALITY_API_KEY"])
            response = request.text
        except:
            print("Error in airqualiity api request.")
        return response

    # override parent method: implement feature
    def _convert_to_obj(self, response):
        my_dict = json.loads(response)
        # peel json layers
        # lat and lon data
        coord = my_dict['coord']
        # dictionary of many data, used for time stamp
        lists = my_dict['list'][0]
        # air quality data set
        main = my_dict['list'][0]['main']
        # different poison gas data set
        components = my_dict['list'][0]['components']
        # put all seperated data in to one neat dict
        alldict = {}

        def put_into_onedic(a_dict):
            for key in a_dict:
                if key == 'main' or key == 'components':
                    continue
                alldict[key] = a_dict[key]

        put_into_onedic(coord)
        put_into_onedic(lists)
        put_into_onedic(main)
        put_into_onedic(components)
        # print(alldict)
        alldiclist = [
            alldict]  # put the neat dict into a list, would be easy for for loop
        # turn all the keys into class object
        object_list = []
        for d in alldiclist:
            object_list.append(AirQuality(d))

        return object_list

    # override parent method: implement feature
    def _create_tables(self):
        # create database if not exists
        sql1 = """CREATE  DATABASE IF NOT EXISTS dublinbikesdb"""
        self._engine.execute(sql1)

        # create the table for air quality data
        sql2 = """CREATE TABLE IF NOT EXISTS airquality(
                    lat FLOAT,
                    lon FLOAT,
                    date DATETIME,
                    aqi INTEGER,
                    co FLOAT,
                    no FLOAT,
                    no2 FLOAT,
                    o3 FLOAT,
                    so2 FLOAT,
                    pm25 FLOAT,
                    pm10 FLOAT,
                    nh3 FLOAT
                    )"""

        try:
            res2 = self._engine.execute(sql2)
            print(res2.fetchall())
        except Exception as e:
            print(e)

    # override parent method: implement feature
    def _save_to_db(self, air_quality_list):
        # clean the table before updating latest aqi data
        sql3 = "DELETE FROM airquality"
        try:
            res3 = self._engine.execute(sql3)
            print(res3.fetchall())
        except Exception as e:
            print(e)
        # insert data into table
        for item in air_quality_list:
            if item.dt:
                TimeDate = datetime.datetime.fromtimestamp(item.dt)
                datetime_str = TimeDate.strftime('%Y-%m-%d %H:%M:%S')
            vals = (
                item.lat, item.lon, datetime_str, item.aqi, item.co, item.no,
                item.no2, item.o3, item.so2, item.pm2_5, item.pm10, item.nh3
            )
            self._engine.execute(
                "insert into airquality values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                vals)


if __name__ == "__main__":
    s = AirQualityScraper(Config().load())
    s.scrape()
