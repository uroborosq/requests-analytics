import datetime


class TitleBuilder:
    def __init__(self):
        self.__string__ = ""

    def join(self, s: str):
        self.__string__ += s

    def add_time_period(self, date_begin: datetime.date, date_end: datetime.date):
        if date_begin == datetime.date.min and date_end == datetime.date.max:
            self.__string__ += "\nв период за все время"
        elif date_begin == datetime.date.min:
            self.__string__ += f"\nв период по {date_end}"
        elif date_end == datetime.date.max:
            self.__string__ += f"\nв период с {date_begin}"
        else:
            self.__string__ += f"\nв период с {date_begin} по {date_end}"

    def add_manager(self, manager: str):
        if manager == 'Все':
            self.__string__ += "\nВсе сотрудники"
        else:
            self.__string__ += f"\n{manager}"

    def add_excluding(self):
        self.__string__ += "\n Внутренние заявки исключены"

    def build(self):
        return self.__string__


class DefaultTitleBuilder:
    def __init__(self, s: str, date_begin: datetime.date, date_end: datetime.date, manager: str, is_excluded: bool):
        builder = TitleBuilder()
        builder.join(s)
        builder.add_time_period(date_begin, date_end)
        builder.add_manager(manager)
        if is_excluded:
            builder.add_excluding()
        self.__result__ = builder.build()

    def build(self):
        return self.__result__

