import os
import pickle

from dublinbikes.common.Config import Config
from dublinbikes.common.DBManager import DBManager
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import pandas as pd

from dublinbikes.ml import DataPreparation


class Prediction:

    def __init__(self, config):
        # set dataframe to let it show all columns
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', -1)
        self._config = config
        self._conn = DBManager(self._config).engine()
        self._DAYS_OF_DATA = 30
        self._bike_df = None
        self._weather_df = None
        self._prepared_df_list = None
        self._model_path = config["MODEL_PATH"]


    def _load_data(self):
        # date function reference: https://www.w3schools.com/sql/func_mysql_adddate.asp
        weather_sql = "select * from dynamic" \
                      f" where last_update > ADDDATE(CURDATE(), INTERVAL -{self._DAYS_OF_DATA} DAY)"
        self._bike_df = pd.read_sql(weather_sql, self._conn)
        self._bike_df.info()
        print("Bike data shape:", self._bike_df.shape)
        print("Bike data head:\n", self._bike_df.head())

        weather_sql = "select * from hourlyWeather_hist" \
                      f" where date_time > ADDDATE(CURDATE(), INTERVAL -{self._DAYS_OF_DATA} DAY)"
        self._weather_df = pd.read_sql(weather_sql, self._conn)
        self._weather_df.info()
        print("Weather data shape:", self._weather_df.shape)
        print("Weather data head:\n", self._weather_df.head())

    def _prepare_data(self):
        station_df_list = DataPreparation.clean_bike_data(self._bike_df)
        self._weather_df = DataPreparation.clean_weather_data(self._weather_df)
        combined_df_list = DataPreparation.join_bike_weather_data(station_df_list, self._weather_df)
        self._prepared_df_list = DataPreparation.derive_feature(combined_df_list)

    def _train_model(self):
        for prepared_df in self._prepared_df_list:
            station_number = int(prepared_df['number'][0])
            print(f'start training station {station_number}')
            train_input_df = prepared_df.drop(['index', 'id', 'index', 'last_update', 'number', 'available_bikes',
                                               'available_bike_stands'], axis=1)
            # train_input_df = prepared_df[['hour', 'day', 'day_time']]
            train_output_df = prepared_df['available_bikes']
            X_train, X_test, y_train, y_test = train_test_split(train_input_df, train_output_df,
                                                                test_size=0.2, random_state=7)
            print(len(X_train), len(X_test), len(y_train), len(y_test))
            print(f'X_train: \n{X_train}')
            print(f'y_train: \n{y_train}')
            regr = LinearRegression()
            regr.fit(X_train, y_train)
            pred = regr.predict(X_test)
            score = regr.score(X_test, y_test)
            r2_sc = r2_score(y_test, pred)
            print('score=', score, ', r2_score=', r2_sc)
            print('save model to pickle file for station:', station_number)
            self._export_model(regr, station_number, 'bikes')

        for prepared_df in self._prepared_df_list:
            station_number = int(prepared_df['number'][0])
            print(f'start training station {station_number}')
            train_input_df = prepared_df.drop(['index', 'id', 'index', 'last_update', 'number', 'available_bikes',
                                               'available_bike_stands'], axis=1)
            # train_input_df = prepared_df[['hour', 'day', 'day_time']]
            train_output_df = prepared_df['available_bike_stands']
            X_train, X_test, y_train, y_test = train_test_split(train_input_df, train_output_df,
                                                                test_size=0.2, random_state=7)
            print(len(X_train), len(X_test), len(y_train), len(y_test))
            print(f'X_train: \n{X_train}')
            print(f'y_train: \n{y_train}')
            regr = LinearRegression()
            regr.fit(X_train, y_train)
            pred = regr.predict(X_test)
            score = regr.score(X_test, y_test)
            r2_sc = r2_score(y_test, pred)
            print('score=', score, ', r2_score=', r2_sc)
            print('save model to pickle file for station:', station_number)
            self._export_model(regr, station_number, 'bike_stands')

    def _export_model(self, model, station_number, type):
        path = f'{self._model_path}/{type}'
        if not os.path.exists(path):
            print(f'path {path} does not exist. create now.')
            os.mkdir(path)
        print(f'start export pickle files for model {type}.')
        pickle.dump(model, open(f'{path}/{station_number}', 'wb'))

    def start(self):
        self._load_data()
        self._prepare_data()
        self._train_model()


if __name__ == "__main__":
    predict = Prediction(Config().load())
    predict.start()
