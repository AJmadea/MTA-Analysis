from urllib.error import HTTPError
import pandas as pd
from datetime import datetime, timedelta
import DataframeModification as dfm


def get_n_latest_mta_dataframes(number):
    df = []
    dates = find_saturday_dates_strings(number)
    return get_data_from_date_string_list(dates)


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


def get_saturday_string_from_date(date):
    if type(date) is str:
        date = get_last_saturday_from_date(date)

    return date.isoformat().replace('-', '')[2:]





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


def find_last_saturday_string():
    return findLastSaturdayDate().isoformat().replace('-', '')[2:]


def get_last_saturday_from_date(date):
    # Convert string to date  if date is of string
    if type(date) is str:
        date = datetime.fromisoformat(date).date()

    # date must be before today
    assert date < datetime.today().date()

    # date must be a saturday (6)
    # if the date is not a saturday, then the last satruday will be used
    day = date.isoweekday()
    if day != 6:
        delta = -1 if day == 7 else -(day + 1)
        date = date + timedelta(days=delta)
    return date


def get_last_saturday_string_from_date(date):
    return get_last_saturday_from_date(date).isoformat().replace('-', '')[2:]


def find_data_from_date_n_iterations(fromDate, n):
    todayDate = datetime.today().date()
    date = get_last_saturday_from_date(fromDate)

    df = []
    dates = []
    for i in range(0, n):
        tempDate = date + timedelta(days=7*i)
        if tempDate < todayDate: # prevents date ahead of today from being added
            dates.append(tempDate.isoformat().replace('-', '')[2:])
        else:
            print('Unable to read data from date: ', tempDate, ' since it is in the future')

    return get_data_from_date_string_list(dates)


def get_data_from_date_to_date(fromDate, toDate):

    fromSatDate = get_last_saturday_from_date(fromDate)
    toSatDate = get_last_saturday_from_date(toDate)

    assert fromSatDate <= toSatDate, 'fromDate must be < toDate'

    dates = []
    weeks = int((toSatDate - fromSatDate).days / 7)

    for i in range(0, weeks+1):
        dates.append((fromSatDate + timedelta(days=7*i)).isoformat().replace('-', '')[2:])

    print(dates)

    return get_data_from_date_string_list(dates)


def get_data_from_date_string_list(listOfDates):
    df = []
    for d in listOfDates:
        baseURL = "http://web.mta.info/developers/data/nyct/turnstile/turnstile_{}.txt".format(d)
        print('Trying to read info from date: ', d)
        temp = pd.read_csv(baseURL)
        df.append(temp)

    all = pd.concat(df)
    errorColumn = all.columns[-1]
    all.rename({errorColumn: 'EXITS'}, axis=1, inplace=True)
    return all


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


def find_total_rides_per_day(df):
    final = pd.DataFrame()

    for date in df['DATE'].unique():
        temp = df[df['DATE'] == date]
        entries = temp['ENTRIES'].sum()
        exits = temp['EXITS'].sum()
        final = final.append(other={'DATE': date,
                                    'ENTRIES': entries,
                                    'EXITS': exits}, ignore_index=True)
    return final
