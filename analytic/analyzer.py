import re
import enum
from datetime import datetime
from datetime import date
from datetime import timedelta

import pandas as pd


def __sunday__(to_sunday: datetime) -> datetime:
    return to_sunday + timedelta(6 - to_sunday.weekday(), 0, 0, 0, 0, 0, 0)


def __first_month_day__(to_first: datetime) -> datetime:
    return datetime(to_first.year, to_first.month, 1)


class TimePeriod(enum.Enum):
    week = 1
    month = 2


def __fill_gaps_with_zeros__(df: pd.DataFrame, period: TimePeriod) -> pd.DataFrame:
    time_period = None
    match period:
        case TimePeriod.month:
            time_period = "MS"
        case TimePeriod.week:
            time_period = "W"

    idx = pd.date_range(df.index.min(), df.index.max(), freq=time_period)
    return df.reindex(idx, fill_value=0)


def __warranty_divider__(period: timedelta) -> str:
    if timedelta(45, 0, 0, 0, 0) >= period >= timedelta(31, 0, 0, 0, 0):
        return "31-45 дней"
    elif timedelta(30, 0, 0, 0, 0) >= period >= timedelta(16, 0, 0, 0, 0):
        return "16-30 дней"
    elif timedelta(15, 0, 0, 0, 0) >= period >= timedelta(6, 0, 0, 0, 0):
        return "6-15 дней"
    elif timedelta(5, 0, 0, 0, 0) >= period >= timedelta(0, 0, 0, 0, 0):
        return "до 5 дней"
    else:
        return "46+ дней"


class AbstractAnalyzer:
    internal: pd.DataFrame

    def __init__(self, df: pd.DataFrame) -> None:
        self.internal = df

    def get(self) -> pd.Series:
        pass


class ManagersAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.DataFrame:
        return self.internal.groupby(["Исполнитель"])["Исполнитель"].count()


class DoneRequestsWeeksAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.Series | pd.DataFrame:
        done = self.internal[
            (self.internal["Статус"] == "Закрыто")
            & (~pd.isnull(self.internal["Дата окончания работ"]))
        ]
        done.loc[:, "Дата окончания работ"] = done["Дата окончания работ"].apply(
            __sunday__
        )
        done.loc[:, "Дата окончания работ"] = done["Дата окончания работ"].apply(
            lambda x: x.normalize()
        )
        return __fill_gaps_with_zeros__(done.groupby(["Дата окончания работ"]).size(), TimePeriod.week)


class DoneRequestsMonthAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.Series | pd.DataFrame:
        done = self.internal[
            (self.internal["Статус"] == "Закрыто")
            & (~pd.isnull(self.internal["Дата окончания работ"]))
        ]
        done["Дата окончания работ"] = done["Дата окончания работ"].apply(
            __first_month_day__
        )
        done["Дата окончания работ"] = done["Дата окончания работ"].apply(
            lambda x: x.normalize()
        )
        return __fill_gaps_with_zeros__(done.groupby(["Дата окончания работ"]).size(), TimePeriod.month)


class ReceivedRequestsWeeksAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.Series | pd.DataFrame:
        self.internal["Дата"] = self.internal["Дата"].apply(__sunday__)
        self.internal["Дата"] = self.internal["Дата"].apply(lambda x: x.normalize())

        return __fill_gaps_with_zeros__(self.internal.groupby(["Дата"]).size(), TimePeriod.week)


class ReceivedRequestsMonthAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.Series | pd.DataFrame:
        self.internal["Дата"] = self.internal["Дата"].apply(__first_month_day__)
        self.internal["Дата"] = self.internal["Дата"].apply(lambda x: x.normalize())
        return __fill_gaps_with_zeros__(self.internal.groupby(["Дата"]).size(), TimePeriod.month)


class WaitingRequestAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.Series | pd.DataFrame:
        index = pd.date_range(
            __sunday__(self.internal["Дата"].min()),
            __sunday__(self.internal["Дата окончания работ"].max()),
            freq="W",
        )
        result = pd.Series(0, index=index)

        for index, row in self.internal.iterrows():
            date_begin = row["Дата"].normalize()
            date_end = pd.Timestamp(datetime.today().date())

            if row["Статус"] == "Закрыто":
                date_end = row["Дата окончания работ"]

            if (date_end.weekday() > date_begin.weekday()) & (date_end - date_begin < timedelta(7)):
                continue

            request_time_range = pd.date_range(
                __sunday__(date_begin), __sunday__(date_end) - timedelta(7), freq="W"
            )
            request_time_series = pd.Series(1, index=request_time_range)
            result = result.add(request_time_series, fill_value=0).astype("Int64")

        return __fill_gaps_with_zeros__(result, TimePeriod.week)

    def get_ids(self):
        index = pd.date_range(
            __sunday__(self.internal["Дата"].min()),
            __sunday__(self.internal["Дата окончания работ"].max()),
            freq="W",
        )
        result = pd.Series("", index=index)
        counter = 0
        for index, row in self.internal.iterrows():
            counter += 1
            date_begin = row["Дата"].normalize()
            date_end = pd.Timestamp.today()
            if row["Статус"] == "Закрыто":
                date_end = row["Дата окончания работ"]

            if (date_end.weekday() > date_begin.weekday()) & (date_end - date_begin < timedelta(7)):
                continue

            request_time_range = pd.date_range(
                __sunday__(date_begin), __sunday__(date_end) - (timedelta(7) if date_end.weekday() != 6 else timedelta(0)), freq="W"
            )
            request_time_series = pd.Series(str(index) + " ", index=request_time_range)
            result = result.add(request_time_series, fill_value="").astype(str)
        print(counter)
        return __fill_gaps_with_zeros__(result, TimePeriod.week)


class WaitingRequestMonthsAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.Series | pd.DataFrame:
        index = pd.date_range(
            __first_month_day__(self.internal["Дата"].min()).date(),
            __first_month_day__(self.internal["Дата окончания работ"].max().date()),
            freq="MS",
        )
        result = pd.Series(0, index=index)

        for index, row in self.internal.iterrows():
            date_begin = row["Дата"].date()
            date_end = datetime.today().date()
            if row["Статус"] == "Закрыто":
                date_end = row["Дата окончания работ"].date()

            request_time_range = pd.date_range(
                __first_month_day__(date_begin),
                __first_month_day__(date_end),
                freq="MS",
            )
            request_time_series = pd.Series(1, index=request_time_range)
            result = result.add(request_time_series, fill_value=0).astype("Int64")

        return __fill_gaps_with_zeros__(result, TimePeriod.month)


class AverageTimeAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.Series:
        self.internal = self.internal[
            (self.internal["Статус"] == "Закрыто")
            & (~pd.isnull(self.internal["Дата окончания работ"]))
        ]
        self.internal.reset_index(drop=True, inplace=True)
        self.internal.loc[:, "Длительность"] = abs(
            self.internal["Дата"] - self.internal["Дата окончания работ"]
        )
        self.internal.loc[:, "Дата окончания работ"] = self.internal[
            "Дата окончания работ"
        ].apply(__first_month_day__)
        return self.internal.groupby(["Дата окончания работ"])["Длительность"].mean()


class PhasesAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.Series:
        self.internal = self.internal[self.internal["Статус"] != "Закрыто"]
        return self.internal.groupby("Ссылка.Фаза").size()

    def get_ids(self) -> pd.Series:
        return self.internal.sort_values(by="Ссылка.Фаза")["Ссылка.Фаза"]


class WarrantyAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.Series:
        self.internal = self.internal[
            (self.internal["Ссылка.Гарантийность"] == "Гарантия")
            & (self.internal["Статус"] != "Закрыто")
        ]
        self.internal.loc[:, "Дата"] = self.internal["Дата"].apply(
            lambda x: datetime.today() - x
        )
        self.internal.loc[:, "Дата"] = self.internal["Дата"].apply(__warranty_divider__)
        return self.internal.groupby(["Дата"]).size()

    def get_ids(self) -> pd.DataFrame:
        return self.internal.sort_values(by=["Дата"])


class DelayProviderAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.Series | pd.DataFrame:
        return self.internal[
            (self.internal["Ссылка.Гарантийность"] != "Гарантия")
            & (self.internal["Ссылка.Фаза"] == "Заказаны запчасти")
            & (datetime.today() - self.internal["Дата"] >= timedelta(180))
        ]


class TypesAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.Series:
        return self.internal.groupby("Ссылка.Гарантийность").size()


class ClientCounterAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.Series:
        self.internal = self.internal[
            self.internal["Дата"] > datetime(datetime.today().year, 1, 1)
            ]
        return self.internal["Клиент.Головной контрагент"].drop_duplicates()


class DayScheduler(AbstractAnalyzer):
    internal: pd.DataFrame
    __date__: date

    def __init__(self, df: pd.DataFrame, given_date: date):
        super().__init__(
            df
        )
        self.__date__ = given_date

    def get(self) -> pd.Series:
        return self.internal[self.internal["Дата начала работ"] == self.__date__][
                [
                    "Ссылка.Исполнители.Исполнитель",
                    "Ссылка.Гарантийность",
                    "Ссылка.Адрес",
                ]
            ]


class RequestRepeatsAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.Series | pd.DataFrame:

        self.internal = self.internal.reset_index()
        self.internal = self.internal.groupby(["Оборудование", "Ссылка.Адрес"])[["Ссылка", "Дата"]].agg(
            {"Дата": ["max"], "Ссылка": ["size", list]}
        )
        return self.internal[
            (self.internal[('Дата',  'max')] - datetime.today() <= timedelta(45))
            & (self.internal[('Ссылка', 'size')] > 2)
            & (
                ~self.internal.index.get_level_values("Ссылка.Адрес").str.contains(
                    "сц|сервис центр|ремзона", flags=re.IGNORECASE, regex=True
                )
            )
        ].explode(('Ссылка', 'list'))


class PriorityAnalyzer(AbstractAnalyzer):
    def get(self) -> pd.Series:
        done = self.internal[self.internal["Статус"] != "Закрыто"]
        return done.groupby(["Ссылка.Приоритет"]).size()

    def get_ids(self) -> pd.Series:
        data = self.internal[self.internal["Статус"] != "Закрыто"]
        return data.sort_values(by=["Ссылка.Приоритет"])["Ссылка.Приоритет"]


class WorkerType(enum.Enum):
    Manager = 1
    Engineer = 2


class SLAnalyzer(AbstractAnalyzer):
    __sla_time_period__: timedelta
    __worker_type__: WorkerType

    def __init__(self, df: pd.DataFrame, sla: timedelta, worker_type: WorkerType):
        super().__init__(df)
        self.__sla_time_period__ = sla
        self.__worker_type__ = worker_type

    def get(self) -> pd.Series:
        column = None
        if self.__worker_type__ == WorkerType.Engineer:
            column = "Ссылка.Исполнители.Исполнитель"
            self.internal = self.internal.explode(column)
        elif self.__worker_type__ == WorkerType.Manager:
            column = "Исполнитель"

        self.internal = self.internal[self.internal["Статус"] == "Закрыто"]
        sla_done = (
            self.internal[
                abs(self.internal["Дата окончания работ"] - self.internal["Дата"])
                <= self.__sla_time_period__
            ]
            .groupby([column])
            .size()
        )

        all_done = self.internal.groupby([column]).size()
        result = sla_done / all_done * 100
        if len(result) > 1:
            result["Общий"] = sla_done.sum() / all_done.sum() * 100
        return result


class MinDate:
    def __init__(self, df: pd.DataFrame):
        self.date = df["Дата"].min()

    def get(self):
        return self.date
