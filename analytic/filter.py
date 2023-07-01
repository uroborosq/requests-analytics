import datetime
import pandas as pd
import numpy as np
import analytic.analyzer


def manager_time_prefilter_by_date_end(df: pd.DataFrame, manager: str, date_begin: pd.Timestamp,
                                       date_end: pd.Timestamp) -> pd.DataFrame | pd.Series:
    df = df[((df['Исполнитель'] == manager) | (manager == 'Все сотрудники'))]
    df = df[date_end >= df['Дата окончания работ']]
    return df[df['Дата окончания работ'] >= date_begin]


def manager_time_prefilter_by_date_begin(df: pd.DataFrame, manager: str, date_begin: pd.Timestamp,
                                         date_end: pd.Timestamp) -> pd.DataFrame:
    df = df[((df['Исполнитель'] == manager) | (manager == 'Все сотрудники'))]
    df = df[date_end >= df['Дата']]
    return df[df['Дата'] >= date_begin]


def manager_filter(df: pd.DataFrame, manager: str) -> pd.DataFrame:
    return df[(df['Исполнитель'] == manager) | (manager == 'Все сотрудники')]


def time_prefilter_by_date_end(df: pd.DataFrame, date_begin: pd.Timestamp, date_end: pd.Timestamp) -> pd.DataFrame:
    df = df[date_end >= df['Дата окончания работ']]
    return df[df['Дата окончания работ'] >= date_begin]


def time_prefilter_by_date_begin(df: pd.DataFrame, date_begin: pd.Timestamp, date_end: pd.Timestamp) -> pd.DataFrame:
    df = df[date_end >= df['Дата']]
    return df[df['Дата'] >= date_begin]


def current_year_filter_by_date_end(df: pd.DataFrame) -> pd.DataFrame:
    df = df[pd.Timestamp(datetime.date.today().year, 1, 1) <= df['Дата окончания работ']]
    return df[pd.Timestamp(datetime.date.today().year, 12, 31) >= df['Дата окончания работ']]


def current_year_filter_by_date_begin(df: pd.DataFrame) -> pd.DataFrame:
    df = df[pd.Timestamp(datetime.date.today().year, 1, 1) <= df['Дата']]
    return df[pd.Timestamp(datetime.date.today().year, 12, 31) >= df['Дата']]


def internal_requests_filter(df: pd.DataFrame) -> pd.DataFrame:
    return df[df['Ссылка.Гарантийность'] != 'Внутренние работы']


def date_postfilter(df: pd.DataFrame | pd.Series, date_begin: pd.Timestamp, date_end: pd.Timestamp) -> pd.DataFrame | pd.Series:
    df = df[df.index >= date_begin]
    return df[df.index <= analytic.analyzer.__sunday__(date_end)]
