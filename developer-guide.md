# Developer's Guide

## Run the project locally

---

### Prerequisites

The project can be set up and run in most of the modern operating systems. 
There are some automation scripts in /script folder for Linux, the 
other OSes have a simialr process but with different commands.

#### Python

To get started, you should [install Python](https://realpython.com/installing-python/)
on your system. Please install a version no less than 3.8.

After that, you should [install pip](https://pip.pypa.io/en/stable/installation/)
for managing python packages.

#### Conda

Conda is used to manage the python virtual environments. This project 
creates and run in a virtual environment named comp30830-dublinbikesPy39.

- Install Conda

  [Miniconda](https://docs.conda.io/en/latest/miniconda.html) is the 
recommended version since it's light-weight.

- Install Conda environment and pip packages by running the command.
```
cd scripts
./install.sh
```
If you already installed the environment and want to reinstall it, run the
command `./uninstall.sh` and `./scripts/install.sh`.

#### Database

An instance of MySql is required.
1. Download [MySQL](https://dev.mysql.com/downloads/) and install it.
2. Start MySQL server and create a database with name `dublinbikesdb`.

### Create the project in IDE

1. Clone the project from github, make sure the folder name is 
   <b>DublinBikes</b> as it's used by the project configurations.

2. Open the project by your favorite IDE. PyCharm from Intellij is a nice one.

3. Set the Python Interpreter of the project to `comp30830-dublinbikesPy39` in
   IDE. For instance, you can find the settings in PyCharm at Preferences | 
   Project: DublinBikes | Python Interpreter. Don't forget to apply before save!

   *If you don't use PyCharm, you may need to set the python path manually.
   Search online about the details.*

4. Update the database connection parameters in section `database` in
   `dublinbikes/common/config.txt`.

5. Right click dublinbikes/scraper/main.py and run the program, if you see 
   logs like below in the console we can move to the next step.
```text
sys.path [***]
current path of Config /dublinbikes/common/config.txt
Final path for config: /***/DublinBikes/dublinbikes/common/config.txt
INFO: Open config file /***/DublinBikes/dublinbikes/common/config.txt
Using the custom config.
main: now is 2022-05-12 14:45:25.771389
```
Ignore the error below if you see. We will fix it later.
```text
INFO: start bike_station_scraper.scrape()
INFO: before requesting API
INFO: after requesting API
INFO: before converting to object
Error: error in main, message: string indices must be integers
```

### Run the scrappers

1. Scrappers need access to JCDecaux, OpenWeatherMap by means of APIKey. 
   They can be requested at [JCDecaux developer](https://developer.jcdecaux.com/#/opendata/vls?page=getstarted) [OpenWeatherMap](https://openweathermap.org/price) (Sign up with a college
   email will be granted with a free APIKey. Please subscribe to
   _Current Weather Data_ and _Air Pollution API_).

2. Update the APIKeys for below sections in `dublinbikes/common/config.txt`.
   - Bike stations
   - Weather
   - Data quality

3. Right click dublinbikes/scraper/main.py and run the program, you will see
the logs at the minutes in multiples of 5.
```text
INFO: start bike_station_scraper.scrape()
INFO: before requesting API
INFO: after requesting API
INFO: before converting to object
INFO: after converting to object
INFO: before creating tables
2022-05-12 15:15:50,971 INFO sqlalchemy.engine.Engine SELECT @@sql_mode
...
...
2022-05-12 15:15:51,400 INFO sqlalchemy.engine.Engine insert into dynamicCurrent values(%s,%s,%s,%s)
2022-05-12 15:15:51,400 INFO sqlalchemy.engine.Engine [raw sql] ('2022-05-12 15:14:14', 88, 21, 9)
2022-05-12 15:15:51,401 INFO sqlalchemy.engine.Engine COMMIT
INFO: after saving to database
INFO: end bike_station_scraper.scrape()
```

4. Now let the main.py scrapper run for a few days to collect enough data for
   machine learning.

> Note: You can also test the scrappers separately by running corresponding
> programs.
> 
>   - dublinbikes/scraper/airquality/AirQualityScraper.py
>   - dublinbikes/scraper/bikes/BikeStationScraper.py
>   - dublinbikes/scraper/weather/WeatherScraper.py

### Run the web application

1. Prepare the Google map api key. **TODO Clarence to add more details**

2. Run the flask application dublinbikes/web/app.py and access the URL printed
in the logs. It's a URL with port 5000 like http://192.168.0.187:5000/.

> Note: Since the machine learning is not ready, the predictions won't work
> at this time.

### Run the machine learning model

Once there are a few hours' data in the tables, we can train the machine
learning model for prediction.

1. Change the `MODEL_PATH` configuration in `dublinbikes/common/config.txt`.
   Make sure the folder exists in your file system.

2. Run machine learning program `dublinbikes/ml/Prediction.py`. Pickle files 
   will be generated in the `MODEL_PATH`.

3. Now you can check the prediction functionality in the web application.

Good luck!

---

Any questions or suggestions please raise in the issues section on the top.
