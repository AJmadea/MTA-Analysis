from urllib.error import HTTPError
import pandas as pd
from datetime import datetime, timedelta
import DataframeModification as dfm


def get_n_latest_mta_dataframes(number):
    df = []
    dates = find_saturday_dates_strings(number)
    for date in dates:
        baseURL = "http://web.mta.info/developers/data/nyct/turnstile/turnstile_{}.txt".format(date)
        print('Trying to read info from date: ', date)
        temp = pd.read_csv(baseURL)
        df.append(temp)

    all = pd.concat(df)
    errorColumn = all.columns[-1]
    all.rename({errorColumn: 'EXITS'}, axis=1, inplace=True)
    return all


def find_saturday_dates(number):
    assert number >= 1, 'Number has to be > 1'
    saturday = findLastSaturdayDate()
    l = []
    for i in range(0, number):
        l.append(saturday - timedelta(days=7*i))
    return l


def find_saturday_dates_strings(number):
    dates = find_saturday_dates(number)
    strings = []
    for date in dates:
        strings.append(date.isoformat().replace('-', '')[2:])
    return strings


def findLastSaturdayDate():
    saturday = None
    today = datetime.today().date()
    day = today.isoweekday()

    # Ternary Operator to choose the previous saturday
    print('today', today.isoweekday())
    saturday = (today + timedelta(days=-1)) if day == 7 else today + timedelta(days=-(day + 1))
    return saturday


def rides_for_each_station_per_day(df):
    final = pd.DataFrame(data={}, columns=['DATE', 'STATION', 'ENTRIES', 'EXITS'])

    for date in df['DATE'].unique():
        for station in df['STATION'].unique():
            entries = []
            exits  = []
            for division in df['DIVISION'].unique():
                temp = df[(df['DATE'] == date) &
                          (df['STATION'] == station) &
                          (df['DIVISION'] == division)]
                for scp in temp['SCP'].unique():
                    for unit in temp['UNIT'].unique():
                        temp2 = temp[(temp['SCP'] == scp) & (temp['UNIT'] == unit)]
                        if len(temp) != 0:
                            entryList = temp2['ENTRIES'].to_list()
                            exitList = temp2['EXITS'].to_list()
                            entries.append(dfm.find_differences(entryList))
                            exits.append(dfm.find_differences(exitList))
                    print(entries, '\n', exits)
                    final = final.append(other={'DATE': date,
                                                'STATION': station,
                                                'ENTRIES': entries,
                                                'EXITS': exits,
                                                }, ignore_index=True)

    return final


def rides_per_day(dataframe):
    final = pd.DataFrame(data={}, columns=['DATE', 'STATION', 'ENTRIES', 'EXITS', 'DIVISION'])
    totalDate = dataframe['DATE'].nunique()
    k = 0
    for date in dataframe['DATE'].unique():
        k = k + 1
        print("Current Date: ", k, ' / ', totalDate)
        for station in dataframe['STATION'].unique():
            entries = []
            exits = []
            print('Date & Station: {} {}'.format(date, station))
            temp = dataframe[(dataframe['DATE'] == date) & (dataframe['STATION'] == station)]
            for scp in temp['SCP'].unique():
                for unit in temp['UNIT'].unique():
                    temp2 = temp[(temp['SCP'] == scp) & (temp['UNIT'] == unit)]
                    if len(temp) != 0:
                        entryList = temp2['ENTRIES'].to_list()
                        exitList = temp2['EXITS'].to_list()
                        entries.append(dfm.find_differences(entryList))
                        exits.append(dfm.find_differences(exitList))
            print(entries, '\n', exits)
            final = final.append(other={'DATE': date,
                                        'STATION': station,
                                        'ENTRIES': entries,
                                        'EXITS': exits,
                                        }, ignore_index=True)
    return final


def rides_per_day_partition_division(dataframe):
    dataframe['STATION'] = dataframe['STATION'] + " " + dataframe['DIVISION']

    divisions = dataframe['DIVISION'].unique()
    newFrames = []
    for division in divisions:
        newFrames.append(rides_per_day( dataframe[ dataframe['DIVISION'] == division] ))
    return pd.concat(newFrames)


def non_path_rides_per_day(dataframe):
    return rides_per_day(dataframe[dataframe['DIVISION'] != 'PTH'])


def pathRidesPerDay(dataframe):
    return rides_per_day(dataframe[dataframe['DIVISION'] == 'PTH'])


def get_latest_mta_dataframe():
    date = findLastSaturdayDate()
    dateString = date.isoformat().replace('-', '')[2:]
    print('Date To be used: ', date, '\ndate string: ', dateString)
    try:
        baseURL = "http://web.mta.info/developers/data/nyct/turnstile/turnstile_{}.txt".format(dateString)
        df = pd.read_csv(baseURL)
    except HTTPError as err:
        print('something went wrong')
    finally:
        # The last column is supposed to be 'EXITS' but it has alot of spaces after it right now
        errorColumn = df.columns[-1]
        df.rename({errorColumn: 'EXITS'}, axis=1, inplace=True)
        return df


def get_nunique_grouped_by_station(rawData):
    listDicts = {}
    allStations = rawData['STATION'].unique().tolist()
    for station in allStations:

        temp = rawData[rawData['STATION'] == station]
        tempMap = {}
        for c in temp.columns:
            tempMap.__setitem__(c, temp[c].nunique())
        tempMap.__setitem__('STATION', station)
        listDicts.__setitem__(station, tempMap)

    stationInformation = pd.DataFrame(data={}, columns=rawData.columns)

    for station in allStations:
        stationInformation = stationInformation.append(other=listDicts[station], ignore_index=True)

    stationInformation.set_index('STATION', inplace=True)

    return stationInformation