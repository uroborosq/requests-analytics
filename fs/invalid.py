import pandas


class ErrorLogger:
    __log_path__: str

    def __init__(self, log_path):
        self.__log_path__ = log_path

    def write(self, df: pandas.DataFrame):
        df['Дата', 'Дата окончания работ'].to_csv(self.__log_path__)

