import datetime


class DefaultTitleBuilder:
    def __init__(self):
        self.__string__ = ""

    def join(self, s: str):
        self.__string__ += s

    def add_time_period(self, date_begin: datetime.date, date_end: datetime.date):
        if date_begin == datetime.date.min and date_end == datetime.date.max:
            self.__string__ += "в период за все время"
        elif date_begin == datetime.date.min:
            self.__string__ += f"в период по {date_end}"
        elif date_end == datetime.date.max:
            self.__string__ += f"в период с {date_begin}"
        else:
            self.__string__ += f"в период с {date_begin} по {date_end}"

    def add_manager(self, manager: str):
        if manager == 'Все':
            self.__string__ += "\nВсе сотрудники"
        else:
            self.__string__ += f"\n{manager}"

    def build(self):
        return self.__string__

