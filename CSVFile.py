import DataframeCreation as dfc
import DataframeModification as dfm
import pandas as pd
import AnalyzingGroups as ag
import warnings
import Validation as v
import Graphs as gr
from datetime import datetime
import DatabaseMethods as dbm


def update_with_new_data():
    raw_data = dfc.get_latest_mta_dataframe()
    analyzed_data = ag.analyze(raw_data, 1300, 3)
    analyzed_data.to_csv('data_by_date/dbscan_analysis_{}.csv'.format(dfc.find_last_saturday_string()))
    get_rides_over_time(analyzed_data)


def get_rides_over_time(data):
    rides_over_time = dfc.find_total_rides_per_day(data)
    dbm.connect_execute_rides_over_time(rides_over_time)


def combine_data_find_rides_over_time(fromDate, toDate):
    saturdays = dfc.get_saturday_list(fromDate, toDate)
    base = 'data_by_date/dbscan_analysis_{}.csv'
    allData = [pd.read_csv(base.format(s)) for s in saturdays]
    concatData = pd.concat(allData)
    data = dfc.find_total_rides_per_day(concatData)
    data.to_csv('data_by_date/001_rides_over_time_from_{}_to_{}.csv'.format(saturdays[0], saturdays[-1]))
    return data


def analyze_from_to_piecewise(fromDate, toDate):
    saturdays = dfc.get_saturday_list(fromDate, toDate)
    base = 'data_by_date/dbscan_analysis_{}.csv'

    for saturday in saturdays:
        data = dfc.get_data_from_date(saturday)
        analyzedData = ag.analyze(data, 1300, 3)
        analyzedData.to_csv(base.format(saturday))

    allData = [pd.read_csv(base.format(s)) for s in saturdays]
    concatData = pd.concat(allData)
    concatData.sort_values(by='DATE', inplace=True)

    rides_over_time = create_rides_over_time_csv(concatData)
    dbm.connect_execute_rides_over_time(rides_over_time)
    concatData.to_csv('data_by_date/000_total_dbscan_analysis_{}_to_{}.csv'.format(saturdays[0], saturdays[-1]))


def analyze_path_trains(fileName):
    d = dfc.get_latest_mta_dataframe()
    d = d[d['DIVISION'] == 'PTH']
    stations = d['STATION'].unique().tolist()
    pathTrains = pd.DataFrame()
    data = pd.read_csv(fileName)
    for i in data.index:
        if data.loc[i, 'STATION'] in stations:
            pathTrains = pathTrains.append(data.loc[i, ])
    fileName = fileName.split('_')
    pathTrains.to_csv('data/path_trains_dbscan_analysis_{}.csv'.format(fileName[2]))


def rides_over_time_dbscan(fromDate, toDate, a, b, c, x, y):
    saturdays = dfc.find_saturday_dates_strings(5)
    fromDate = dfc.get_saturday_string_from_date(fromDate)
    toDate = dfc.get_saturday_string_from_date(toDate)

    for eps in range(a, b, c):
        for min_samples in range(x, y):
            fileInput = 'data/dbscan_data_outputs/dbscan_eps={}_min_samples={}_from_{}_to_{}.csv'.format(
                eps, min_samples, fromDate, toDate)

            print('Reading from', fileInput)
            temp = pd.read_csv(fileInput)
            temp = dfc.find_total_rides_per_day(temp)

            fileOutput = 'data/dbscan_over_time/dbscan_over_time_eps={}_min_samples={}_from_{}_to_{}.csv'.format\
                (eps, min_samples, fromDate, toDate)
            print('outputting to:', fileOutput)
            temp.to_csv(fileOutput)


def create_analyze_calculate_error_dbscan(fromDate, toDate, a, b, c, x, y, n):
    analyze_with_different_dbscan_params(a, b, c, x, y, n)
    rides_over_time_dbscan(fromDate, toDate, a, b, c, x, y)
    v.calculate_mse_for_all_dbscan(a, b, c, x, y, fromDate, toDate)

    errors = ['R2', 'MSE', 'MAE']
    attrTypes = ['ENTRIES', 'EXITS']

    for e in errors:
        for a in attrTypes:
            v.graph_errors(startEPS=a, stopEPS=b, stepEPS=c, startSample=x, stopSample=y, fromDate=fromDate, toDate=toDate,
                           whatToGraph='{} {}'.format(e, a))


def create_rides_over_time_csv(df):
    ridesPerDay = dfc.find_total_rides_per_day(df)
    ridesPerDay.sort_values(by='DATE', inplace=True)
    d = dfm.create_date_dictionary_string(df)
    dates = sorted(list(d.keys()))
    fromDate = d.get(dates[0])
    toDate = d.get(dates[-1])

    fileName = 'data/rides_over_time_{}_to_{}.csv'.format(fromDate, toDate)
    print('Trying to save to file: ', fileName)
    ridesPerDay.to_csv(fileName)
    return ridesPerDay


def analyze_with_different_dbscan_params(a, b, c, x, y, n):
    warnings.filterwarnings('ignore')
    rawData = dfc.get_n_latest_mta_dataframes(n)
    saturdays = dfc.find_saturday_dates_strings(n)
    iterations = (b-a)/c * (y - x)
    print('total DBSCAN param iterations:', iterations)
    current = 0

    for eps in range(a, b, c):
        for min_samples in range(x, y):
            analyzedData = ag.analyze(rawData, eps=eps, min_samples=min_samples)
            fileName = 'data/dbscan_data_outputs/dbscan_eps={}_min_samples={}_from_{}_to_{}.csv'.format(
                eps, min_samples, saturdays[-1], saturdays[0])
            analyzedData.to_csv(fileName)
            current += 1
            print(current, '/', iterations)


def analyze_append_new_data_to_csv(fileName, eps, min_samples):
    warnings.filterwarnings('ignore')
    newData = dfc.get_latest_mta_dataframe()
    analyzedNewData = ag.analyze(newData, eps, min_samples)

    oldData = pd.read_csv(fileName)
    newTotal = pd.concat([analyzedNewData, oldData])

    saturday = dfc.find_last_saturday_string()
    newName = 'data/dbscan_analysis_from_{}_to_{}.csv'.format(fileName.split('_')[2], saturday)
    print('Writing out to file: ', newName)
    newTotal.to_csv(newName)


def clean_up_columns(fileName):
    data = pd.read_csv(fileName)
    for column in data.columns:
        if "Unnamed" in column:
            data.drop(columns=column, axis=1, inplace=True)

    data.to_csv(fileName)


def sort_by_date(df, fileName):
    df.sort_values(by='DATE', inplace=True)
    df.to_csv(fileName)


def analyze_from_to_optics(fromDate, toDate):
    warnings.filterwarnings('ignore')
    data = dfc.get_data_between_two_dates(fromDate, toDate)
    dates = sorted(data['DATE'].unique().tolist())
    data = data[data['DESC'] == 'REGULAR']

    analyzedData = ag.analyze_optics(data, 1300)
    fileName = 'data/optics_analysis_from_{}_to_{}.csv'.format(dates[0], dates[-1])
    analyzedData.to_csv(fileName)

    rides_per_day = dfc.find_total_rides_per_day(analyzedData)
    rides_per_day.to_csv('optics_total_rides_over_time_from_{}_to_{}.csv'.format(dates[0], dates[-1]))


def analyze_from_to_dbscan(fromDate, toDate):
    warnings.filterwarnings('ignore')
    data = dfc.get_data_between_two_dates(fromDate, toDate)
    dates = sorted(data['DATE'].unique().tolist())
    data = data[data['DESC'] == 'REGULAR']

    analyzedData = ag.analyze(data, 1300, 3)
    fileName = 'data/dbscan_analysis_from_{}_to_{}.csv'.format(dates[0], dates[-1])
    analyzedData.to_csv(fileName)

    rides_per_day = dfc.find_total_rides_per_day(analyzedData)
    rides_per_day.to_csv('dbscan_total_rides_over_time_from_{}_to_{}.csv'.format(dates[0], dates[-1]))


def analyze_n_dataframes_by_DBSCAN(number):
    data = dfc.get_n_latest_mta_dataframes(number)
    saturdays = dfc.find_saturday_dates_strings(number)
    data = data[data['DESC'] == 'REGULAR']
    analyzedData = ag.analyze(data, 1300, 3)
    print(ag.count_negative_groups(analyzedData))
    analyzedData.to_csv('data/dbscan_analysis_{}_to_{}.csv'.format(saturdays[-1], saturdays[0]))


def analyze_latest_dataframe_by_OPTICS():
    data = dfc.get_latest_mta_dataframe()
    saturday = dfc.find_last_saturday_string()
    data = data[data['DESC'] == 'REGULAR']
    analyzedData = ag.analyze_optics(data, 1300)
    analyzedData.to_csv('data/optics_analysis_{}.csv'.format(saturday))


def analyze_latest_dataframe_by_DBSCAN_():
    data = dfc.get_latest_mta_dataframe()
    saturday = dfc.find_last_saturday_string()
    data = data[data['DESC'] == 'REGULAR']
    analyzedData = ag.analyze(data, 1300, 3)
    analyzedData.to_csv('data/dbscan_analysis_{}.csv'.format(saturday))


def analyze_latest_dataframe_by_DBSCAN(station):
    data = dfc.get_latest_mta_dataframe()
    saturday = dfc.find_last_saturday_string()
    data = data[data['STATION'] == station]
    analyzedData = ag.analyze(data)
    analyzedData.to_csv('data/dbscan_analysis_of_{}_{}.csv'.format(station, saturday))
