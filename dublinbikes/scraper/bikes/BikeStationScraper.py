import datetime
import json
import requests

from dublinbikes.common.Config import Config
from dublinbikes.scraper.base.WebScraper import WebScraper


class BikeStationInfo:
    def __init__(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])


class BikeStationScraper(WebScraper):
    def __init__(self, config):
        WebScraper.__init__(self, config)

    # override parent method: implement feature
    def _request_api(self):
        request = requests.get(self._config["STATIONS"],
                               params={"apiKey": self._config["APIKEY"],
                                       "contract": self._config["NAME"]})
        response = request.text
        return response

    # override parent method: implement feature
    def _convert_to_obj(self, response):
        station_dicts = json.loads(response)
        # turn it into Weather object
        station_list = []
        for station_dict in station_dicts:
            station_list.append(BikeStationInfo(station_dict))
        return station_list

    # override parent method: implement feature
    def _create_tables(self):
        # create database if not exists
        sql1 = """CREATE  DATABASE IF NOT EXISTS dublinbikesdb"""
        self._engine.execute(sql1)

        # create the table for static data
        sql2 = """CREATE TABLE IF NOT EXISTS static (
                    name VARCHAR(256),
                    number INTEGER,
                    position_lat REAL,
                    position_lng REAL,
                    banking BOOLEAN,
                    bonus BOOLEAN,
                    bike_stands INTEGER,
                    status  VARCHAR(256)
                    )"""

        try:
            res1 = self._engine.execute(sql2)
        except Exception as e:
            print(e)

        # create the table for historical dynamic data
        sql3 = """CREATE TABLE IF NOT EXISTS dynamic (
                    last_update DATETIME,
                    number INTEGER,
                    available_bike_stands INTEGER,
                    available_bikes INTEGER
                    )"""

        try:
            res2 = self._engine.execute(sql3)
        except Exception as e:
            print(e)
        
        # create the table for current dynamic data
        sql4 = """CREATE TABLE IF NOT EXISTS dynamicCurrent (
                    last_update DATETIME,
                    number INTEGER,
                    available_bike_stands INTEGER,
                    available_bikes INTEGER
                    )"""

        try:
            res3 = self._engine.execute(sql4)
        except Exception as e:
            print(e)

    # override parent method: implement feature
    def _save_to_db(self, bike_stations):
        self._static_to_db(bike_stations)
        self._dynamic_to_db(bike_stations)
        self._dynamicCurrent_to_db(bike_stations)

    # insert the static data into table 'static', take one parameter
    # 'static_data', which is in list type (contians a list of dicts)
    def _static_to_db(self, static_data):
        print("delete static_data")
        # clean the table before updating static data
        sql4 = "DELETE FROM static"
        try:
            res3 = self._engine.execute(sql4)
        except Exception as e:
            print(e)

        # insert data
        print("save static_data")
        for item in static_data:
            print(item)
            vals = (
                item.name, int(item.number), item.position['lat'],
                item.position['lng'], item.banking, item.bonus,
                int(item.bike_stands), item.status
            )
            self._engine.execute(
                "insert into static (name, number, position_lat, position_lng, banking, bonus, bike_stands, status) values(%s,%s,%s,%s,%s,%s,%s,%s)", vals)
        return

    # insert the dynamic data into table 'dynamic', take one parameter
    # 'dynamic_data', which is in list type (contains a list of dicts)
    def _dynamic_to_db(self, dynamic_data):
        print("save historical dynamic_data")
        for item in dynamic_data:
            if item.last_update:
                epoch_time = int(item.last_update) / 1000
                TimeDate = datetime.datetime.fromtimestamp(epoch_time)
                datetime_str = TimeDate.strftime('%Y-%m-%d %H:%M:%S')
            vals = (
                datetime_str, int(item.number),
                int(item.available_bike_stands), int(item.available_bikes)
            )
            self._engine.execute(
                "insert into dynamic values(%s,%s,%s,%s)", vals)
        return

    # insert the dynamic data into table 'dynamicCurrent', take one parameter
    # 'dynamic_data', which is in list type (contains a list of dicts)
    def _dynamicCurrent_to_db(self, dynamic_data):
        print("delete current dynamic_data")
        # clean the table before updating latest dynamic data
        sql = "DELETE FROM dynamicCurrent"
        try:
            res = self._engine.execute(sql)
        except Exception as e:
            print(e)

         # insert data
        print("save current dynamic_data")
        for item in dynamic_data:
            if item.last_update:
                epoch_time = int(item.last_update) / 1000
                TimeDate = datetime.datetime.fromtimestamp(epoch_time)
                datetime_str = TimeDate.strftime('%Y-%m-%d %H:%M:%S')
            vals = (
                datetime_str, int(item.number),
                int(item.available_bike_stands), int(item.available_bikes)
            )
            self._engine.execute(
                "insert into dynamicCurrent values(%s,%s,%s,%s)", vals)
        return
        



if __name__ == "__main__":
    s = BikeStationScraper(Config().load())
    s.scrape()

