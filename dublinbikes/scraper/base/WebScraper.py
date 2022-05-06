from dublinbikes.common.Config import Config
from dublinbikes.common.DBManager import DBManager


class WebScraper:
    def __init__(self, config):
        if config is None:
            self._config = Config().load()
        else:
            print("Using the custom config.")
            self._config = config
        self._engine = None

    def scrape(self):
        print("INFO: before requesting API")
        response = self._request_api()
        print("INFO: after requesting API")

        print("INFO: before converting to object")
        data_obj = self._convert_to_obj(response)
        print("INFO: after converting to object")

        # get database connection every time
        self._engine = DBManager(self._config).engine()

        print("INFO: before creating tables")
        self._create_tables()
        print("INFO: after creating tables")

        print("INFO: before saving to database")
        self._save_to_db(data_obj)
        print("INFO: after saving to database")

    # need to be overridden by subclass
    def _request_api(self):
        return None

    # need to be overridden by subclass
    def _convert_to_obj(self, response):
        return None

    # need to be overridden by subclass
    def _create_tables(self):
        pass

    # need to be overridden by subclass
    def _save_to_db(self, data_obj):
        pass
