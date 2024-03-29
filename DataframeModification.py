import numpy as np
from datetime import date as dt
import pandas as pd


def add_ridership_column(data):
    for i in data.index:
        entry = data.loc[i, 'ENTRIES']
        _exit = data.loc[i, 'EXITS']
        _max = max(entry, _exit)
        _min = min(entry, _exit)
        data.loc[i, 'RIDERSHIP'] = _max + (_max - _min)


def create_date_dictionary(df):
    d = {}
    dates = df['DATE'].unique()
    for date in dates:
        string = '{}-{}-{}'.format(date[6:], date[0:2], date[3:5])
        d[date] = dt.fromisoformat(string)
    return d


def create_date_dictionary_string(df):
    d = {}
    dates = df['DATE'].unique()
    for date in dates:
        string = '{}-{}-{}'.format(date[6:], date[0:2], date[3:5])
        d[date] = string
    return d


def add_date_related_columns(df):
    d = create_date_dictionary(df)
    print("Iterating through each index...")
    for i in df.index:
        newDate = d.get(df.loc[i, 'DATE'])
        df.loc[i, 'ISOWEEKDAY'] = newDate.isoweekday()
        df.loc[i, 'MONTH'] = newDate.month
        df.loc[i, 'DAY'] = newDate.day
        df.loc[i, 'YEAR'] = newDate.year
    return df


def drop_weekends(df):
    if 'ISOWEEKDAY' not in df.columns:
        df = get_isodate_number(df)

    return df[df['ISOWEEKDAY'] >= 6]


def drop_weekdays(df):
    if 'ISOWEEKDAY' not in df.columns:
        df = get_isodate_number(df)

    return df[df['ISOWEEKDAY'] < 6]


def weekend_dependent_split(df):
    if 'ISOWEEKDAY' not in df.columns:
        df = get_isodate_number(df)

    weekends = df[df['ISOWEEKDAY'] >= 6]
    weekdays = df[df['ISOWEEKDAY'] < 6]

    return weekdays, weekends


def get_isodate_number(df):
    #                       0123456789
    # create dictionary of 'MM/DD/YYYY' KEY to YYYY-MM-DD VALUE
    dates = df['DATE'].unique()
    d = {}
    for date in dates:
        string = '{}-{}-{}'.format(date[6:], date[0:2], date[3:5])
        d.__setitem__(date, dt.fromisoformat(string).isoweekday())

    for i in df.index:
        df.loc[i, 'ISOWEEKDAY'] = d.get(df.loc[i, 'DATE'])

    return df


def find_differences(dlist):
    if len(dlist) <= 1:
        return 0

    diff = 0
    t = [dlist[0]]
    for n in range(0, len(dlist)):
        if t[-1] <= dlist[n]:
            t.append(dlist[n])
        else:
            diff = diff + t[-1] - t[0]
            t.clear()
            t.append(dlist[n])
    if len(t) == 1:
        diff = diff + t[0]
    else:
        diff = diff + t[-1] - t[0]
    return diff


def combine_newark(df):
    stations = df['STATION'].unique().tolist()

    newarkStations = []
    for s in stations:
        if 'NEWARK' in s:
            newarkStations.append(s)
            stations.remove(s)

    newarkStations.append("NEWARK C")
    stations.remove('NEWARK C')

    print('Newark Stations : ', newarkStations)
    stations.append("NEWARK")
    print('Non-newark stations: ', stations)
    for date in df['DATE'].unique():
        entries = 0
        exits = 0
        for station in newarkStations:
            temp = df[(df['DATE'] == date) & (df['STATION'] == station)]
            entries = entries + temp['ENTRIES'].to_numpy().sum()
            exits = exits + temp['EXITS'].to_numpy().sum()

        # print("Appending: ", "{} {} {}".format(date, entries, exits))
        df = df.append(other={'STATION': "NEWARK",
                              'DATE': date,
                              'ENTRIES': entries,
                              'EXITS': exits
                              }, ignore_index=True)

    print('Before mod ', df.shape)

    for i in df.index:
        if df.loc[i, 'STATION'] in newarkStations:
            df.drop(index=i, axis=0, inplace=True)

    print('After mod ', df.shape)
    return df


def combine_wtc(df):
    stations = df['STATION'].unique().tolist()

    wtcStations = ['PATH WTC 2', 'PATH NEW WTC']
    for s in wtcStations:
        if s in stations:
            stations.remove(s)

    print('WTC Stations : ', wtcStations)
    stations.append("WTC")
    print('Non-WTC stations: ', stations)

    for date in df['DATE'].unique():
        entries = 0
        exits = 0
        for station in wtcStations:
            temp = df[(df['DATE'] == date) & (df['STATION'] == station)]
            entries = entries + temp['ENTRIES'].to_numpy().sum()
            exits = exits + temp['EXITS'].to_numpy().sum()

        # print("Appending: ", "{} {} {}".format(date, entries, exits))
        df = df.append(other={'STATION': "WTC",
                              'DATE': date,
                              'ENTRIES': entries,
                              'EXITS': exits
                              }, ignore_index=True)

    print('Before mod ', df.shape)

    for i in df.index:
        if df.loc[i, 'STATION'] in wtcStations:
            df.drop(index=i, axis=0, inplace=True)

    print('After mod ', df.shape)
    return df


def entry_exit_ratio(df):
    df['ENTRIES/EXITS'] = df['ENTRIES'] / df['EXITS']
    return df


def combine_similar_rows(df):
    df = combine_wtc(df)
    df = combine_newark(df)
    return df


def create_datetime_objects(df):
    map = create_date_dictionary_string(df)
    df['DATE TIME'] = ' '
    for i in df.index:
        datetemp = map.get(df.loc[i, 'DATE'])
        timetemp = df.loc[i, 'TIME']
        dateTimeString = '{} {}'.format(datetemp, timetemp)
        df.loc[i, 'DATE TIME'] = dt.fromisoformat(dateTimeString)
    return df


