from sqlalchemy import create_engine


class DBManager:
    def __init__(self, config):
        # if config is None:
        #     self._config = Config().load()
        # else:
        #     self._config = config
        self._config = config
        self.db = self._config["DB"]
        self.db_user = self._config["USER"]
        self.db_password = self._config["PASSWORD"]
        self.db_url = self._config["URL"]
        self.db_port = self._config["PORT"]

    def engine(self):
        # connect to database and return the connection
        return create_engine(
            "mysql+pymysql://{}:{}@{}:{}/{}".format(self.db_user,
                                                    self.db_password,
                                                    self.db_url,
                                                    self.db_port,
                                                    self.db), echo=True)
