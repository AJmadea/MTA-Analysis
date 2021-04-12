import pandas as pd


def get_top_n_stations_per_date(frame, n):
    dates = frame['DATE'].unique().tolist()

    stats = pd.DataFrame()
    map = {}
    for date in dates:
        map.__setitem__('DATE', date)
        temp = frame[frame['DATE'] == date]
        temp.reset_index(inplace=True)
        entrySorted = temp.sort_values(ascending=False, by='ENTRIES')
        exitSorted = temp.sort_values(ascending=False, by='EXITS')
        topEntries = entrySorted['STATION'].tolist()[0:n]
        topExits = exitSorted['STATION'].tolist()[0:n]

        for k in range(0, len(topEntries)):
            map.__setitem__('Top Entry #{}'.format(k+1), topEntries[k])

        for k in range(0, len(topExits)):
            map.__setitem__('Top Exits #{}'.format(k+1), topExits[k])

        stats = stats.append(other=map, ignore_index=True)
    return stats


def get_top_station_per_date(frame):
    dates = frame['DATE'].unique().tolist()

    stats = pd.DataFrame()

    for date in dates:
        temp = frame[frame['DATE'] == date]
        temp.reset_index(inplace=True)
        entryLoc = temp['ENTRIES'].argmax()
        exitLoc = temp['EXITS'].argmax()

        stationMaxEntries = temp.loc[entryLoc, 'STATION']
        stationMaxExits = temp.loc[exitLoc, 'STATION']

        stats = stats.append(other={'DATE': date,
                                    'ENTRIES MAX': stationMaxEntries,
                                    'EXITS MAX': stationMaxExits}, ignore_index=True)
    return stats
