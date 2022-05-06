import time
from datetime import datetime

from dublinbikes.scraper.airquality.AirQualityScraper import AirQualityScraper
from dublinbikes.scraper.bikes.BikeStationScraper import BikeStationScraper
from dublinbikes.common.Config import Config
from dublinbikes.scraper.weather.WeatherScraper import WeatherScraper

if __name__ == "__main__":
    # initialize a configuration using the default settings
    config = Config()
    config_dict = config.load()
    # instantiate scrapers
    bike_station_scraper = BikeStationScraper(config_dict)
    weather_scraper = WeatherScraper(config_dict)
    air_quality_scraper = AirQualityScraper(config_dict)

    while True:
        now = datetime.now()
        print("main: now is", now)
        minute = now.minute
        try:
            # scrape bike data every 5 minutes
            if minute % 5 == 0:
                print("INFO: start bike_station_scraper.scrape()")
                bike_station_scraper.scrape()
                print("INFO: end bike_station_scraper.scrape()")

            # scrape weather data every 10 minutes
            if minute % 10 == 0:
                print("INFO: start weather_scraper.scrape()")
                weather_scraper.scrape()
                print("INFO: end weather_scraper.scrape()")

            # scrape air quality data every 10 minutes
            # 6 minutes gap after weather due to the same API limit
            if minute % 10 == 6:
                print("INFO: start air_quality_scraper.scrape()")
                air_quality_scraper.scrape()
                print("INFO: end air_quality_scraper.scrape()")
        except Exception as e:
            print("Error: error in main, message:", e)

        # sleep 1 minutes
        time.sleep(60)

