import pandas as pd
import DataframeModification as dfm
from datetime import datetime as dt
import numpy as np





def get_top_n_covid_affected_stations(data, n, write=False):
    stations = data['STATION'].unique()
    n = n if len(stations) > n else len(stations)

    data.sort_values(by='ENTRY % CHANGE', inplace=True)
    entryChange = data['STATION'].tolist()[0:n]

    data.sort_values(by='EXIT % CHANGE', inplace=True)
    exitChange = data['STATION'].tolist()[0:n]

    data.sort_values(by='ENTRY CHANGE MAGNITUDE', inplace=True)
    entryMagChange = data['STATION'].tolist()[0:n]

    data.sort_values(by='EXIT CHANGE MAGNITUDE', inplace=True)
    exitMagChange = data['STATION'].tolist()[0:n]

    print('Top ', n, '% Change in Entries: ', entryChange)
    print('Top ', n, '% Change in Exits: ', exitChange)
    print('Top ', n, 'Magnitude of Entry Change: ', entryMagChange)
    print('Top ', n, 'Magnitude of Exit Change: ', exitMagChange)

    if write:
        pd.DataFrame(data={'Top {} Change in Entries (%)'.format(n): entryChange,
                           'Top {} Change in Exits (%)'.format(n): exitChange,
                           'Top {} Change in Entries (Magnitude)'.format(n): entryMagChange,
                           'Top {} Change in Exits (Magnitude)'.format(n): exitMagChange}).\
            to_csv('data_by_date/top_covid_change.csv')

    allStations = set({})
    for l in [entryChange, exitChange, entryMagChange, exitMagChange]:
        for e in l:
            allStations.add(e)
    return allStations


def get_change_from_covid19():
    after = pd.read_csv('data_by_date/after_covid19.csv')
    before = pd.read_csv('data_by_date/before_covid19.csv')

    for i in after.index:
        if after.loc[i, 'MONTH'] == 3:
            if after.loc[i, 'DAY'] < 11:
                after.drop(index=i, axis=0, inplace=True)

    stations = np.intersect1d(after['STATION'].unique(),
                              before['STATION'].unique())

    stationList = []
    entryAvgBefore = []
    exitAvgBefore = []
    entryAvgAfter = []
    exitAvgAfter = []

    for station in stations:
        stationList.append(station)
        afterPart = after[after['STATION'] == station]

        entryAvgAfter.append(afterPart['ENTRIES'].mean())
        exitAvgAfter.append(afterPart['EXITS'].mean())

        beforePart = before[before['STATION'] == station]
        entryAvgBefore.append(beforePart['ENTRIES'].mean())
        exitAvgBefore.append(beforePart['EXITS'].mean())

    print(stationList, '\n', entryAvgAfter, '\n', entryAvgBefore)

    changeDf = pd.DataFrame(data={'STATION': stationList,
                                  'ENTRY AVG BEFORE': entryAvgBefore,
                                  'EXIT AVG BEFORE': exitAvgBefore,
                                  'ENTRY AVG AFTER': entryAvgAfter,
                                  'EXIT AVG AFTER': exitAvgAfter
                            }, index=stations,
                            columns=['STATION', 'ENTRY AVG BEFORE',
                                     'EXIT AVG BEFORE', 'ENTRY AVG AFTER', 'EXIT AVG AFTER'])

    changeDf['ENTRY CHANGE MAGNITUDE'] = changeDf['ENTRY AVG AFTER'] - changeDf['ENTRY AVG BEFORE']
    changeDf['EXIT CHANGE MAGNITUDE'] = changeDf['EXIT AVG AFTER'] - changeDf['EXIT AVG BEFORE']

    changeDf['ENTRY % CHANGE'] = changeDf['ENTRY CHANGE MAGNITUDE'] / changeDf['ENTRY AVG BEFORE'] * 100
    changeDf['EXIT % CHANGE'] = changeDf['EXIT CHANGE MAGNITUDE'] / changeDf['EXIT AVG BEFORE'] * 100

    changeDf.sort_values(by='ENTRY % CHANGE', inplace=True)

    changeDf.to_csv('data_by_date/statFrame.csv')


def partition_change_from_covid19(df):
    # Magnitude of decrease in ridership
    # % Change in ridership
    df = dfm.add_date_related_columns(df)
    print(df.shape)
    df['DATE'] = df['DATE'].astype('str')
    before = pd.DataFrame()
    after = pd.DataFrame()
    print(df.head())

    print(df.columns)
    df.to_csv('data_by_date/date_mods.csv')
    after = df[(df['MONTH'] == 3) & (df['YEAR'] == 2020)]
    before = df[(df['MONTH'] <= 2) & (df['YEAR'] == 2020)]
    after.to_csv('data_by_date/after_covid19.csv')
    before.to_csv('data_by_date/before_covid19.csv')


def get_top_n_stations_per_date(dataframe, n):
    dates = dataframe['DATE'].unique().tolist()

    stats = pd.DataFrame()
    map12 = {}
    for date in dates:
        map12.__setitem__('DATE', date)
        temp = dataframe[dataframe['DATE'] == date]
        temp.reset_index(inplace=True)
        entrySorted = temp.sort_values(ascending=False, by='ENTRIES')
        exitSorted = temp.sort_values(ascending=False, by='EXITS')
        topEntries = entrySorted['STATION'].tolist()[0:n]
        topExits = exitSorted['STATION'].tolist()[0:n]

        for k in range(0, len(topEntries)):
            map12.__setitem__('Top Entry #{}'.format(k + 1), topEntries[k])

        for k in range(0, len(topExits)):
            map12.__setitem__('Top Exits #{}'.format(k + 1), topExits[k])

        stats = stats.append(other=map12, ignore_index=True)
    return stats


def get_top_station_per_date(dataframe):
    dates = dataframe['DATE'].unique().tolist()

    stats = pd.DataFrame()

    for date in dates:
        temp = dataframe[dataframe['DATE'] == date]
        temp.reset_index(inplace=True)
        entryLoc = temp['ENTRIES'].argmax()
        exitLoc = temp['EXITS'].argmax()

        stationMaxEntries = temp.loc[entryLoc, 'STATION']
        stationMaxExits = temp.loc[exitLoc, 'STATION']

        stats = stats.append(other={'DATE': date,
                                    'ENTRIES MAX': stationMaxEntries,
                                    'EXITS MAX': stationMaxExits}, ignore_index=True)
    return stats
