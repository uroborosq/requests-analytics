import pandas


class ReportBuilder:
    __log_path__: str

    def __init__(self, log_path: str, is_source: bool):
        self.__log_path__ = log_path
        self.__mode__ = "a" if is_source else "w"

    def write_invalid(self, df: pandas.DataFrame):
        column_name = "Ошибки парсинга"
        excel_writer = pandas.ExcelWriter(
            self.__log_path__, engine="openpyxl", mode=self.__mode__
        )
        df.to_excel(excel_writer, sheet_name=column_name)
        # for column in df:
        #     column_length = max(df[column].astype(str).map(len).max(), len(column)) + 10
        #     col_idx = df.columns.get_loc(column)
        #     excel_writer.sheets[column_name].set_column(col_idx, col_idx, column_length)
        excel_writer.close()

    def write_repeats(self, df: pandas.DataFrame):
        excel_writer = pandas.ExcelWriter(
            self.__log_path__, engine="openpyxl", mode="a", if_sheet_exists="replace"
        )
        df.to_excel(excel_writer, sheet_name="Повторы заявок")
        excel_writer.close()

    def write_warranty(self, df: pandas.DataFrame):
        excel_writer = pandas.ExcelWriter(
            self.__log_path__, engine="openpyxl", mode="a", if_sheet_exists="replace"
        )
        df.to_excel(excel_writer, sheet_name="Гарантия")
        excel_writer.close()

    def write_priorities(self, df: pandas.DataFrame):
        excel_writer = pandas.ExcelWriter(
            self.__log_path__, engine="openpyxl", mode="a", if_sheet_exists="replace"
        )
        df.to_excel(excel_writer, sheet_name="Приоритеты")
        excel_writer.close()

    def write_delay(self, df: pandas.DataFrame):
        excel_writer = pandas.ExcelWriter(
            self.__log_path__, engine="openpyxl", mode="a", if_sheet_exists="replace"
        )
        df.to_excel(excel_writer, sheet_name="Просрочки поставщика")
        excel_writer.close()

    def write_phases(self, df: pandas.DataFrame):
        excel_writer = pandas.ExcelWriter(
            self.__log_path__, engine="openpyxl", mode="a", if_sheet_exists="replace"
        )
        df.to_excel(excel_writer, sheet_name="Фазы")
        excel_writer.close()

