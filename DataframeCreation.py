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
    assert number > 1, 'Number has to be > 1'
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
    # -(day % 6 + 1) changes isoformat for each day to the previous saturday
    saturday = (today + timedelta(days=-7)) if day == 6 else today + timedelta(days=-(day % 6 + 1))
    return saturday


def pathRidesPerDay(dataframe):
    final = pd.DataFrame(data={}, columns=['DATE', 'STATION', 'ENTRIES', 'EXITS'])
    dataframe = dataframe[dataframe['DIVISION'] == 'PTH']
    for date in dataframe['DATE'].unique():
        for station in dataframe['STATION'].unique():
            entries = []
            exits = []
            for scp in dataframe['SCP'].unique():
                temp = dataframe[
                    (dataframe['DATE'] == date) & (dataframe['STATION'] == station) & (dataframe['SCP'] == scp)]
                if len(temp) != 0:
                    entryList = temp['ENTRIES'].to_list()
                    exitList = temp['EXITS'].to_list()
                    entries.append(dfm.find_differences(entryList))
                    exits.append(dfm.find_differences(exitList))

            final = final.append(other={'DATE': date,
                                        'STATION': station,
                                        'ENTRIES': entries,
                                        'EXITS': exits
                                        }, ignore_index=True)

    return final


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
