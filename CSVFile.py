import DataframeCreation as dfc
import DataframeModification as dfm
import pandas as pd
import AnalyzingGroups as ag
import warnings


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


def rides_over_time_dbscan(fromDate, toDate, a,b,c,x,y):
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


def analyze_with_different_dbscan_params(a, b, c, x, y,):
    warnings.filterwarnings('ignore')
    rawData = dfc.get_n_latest_mta_dataframes(5)
    saturdays = dfc.find_saturday_dates_strings(5)
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


def analyze_append_new_data_to_csv(fileName):
    newData = dfc.get_latest_mta_dataframe()
    analyzedNewData = ag.analyze(newData)
    oldData = pd.read_csv(fileName)
    newTotal = pd.concat([newData, oldData])

    saturday = dfc.find_last_saturday_string()
    newName = 'pathTrains_{}_to_{}.csv'.format(fileName.split('_')[1], saturday[0])
    print('Writing out to file: ', newName)
    newTotal.to_csv(newName)


def clean_up_columns(fileName):
    data = pd.read_csv(fileName)
    for column in data.columns:
        if "Unnamed" in column:
            data.drop(columns=column, axis=1, inplace=True)

    data.to_csv(fileName)


def append_new_data_to_csv(fileName):
    print("Reading data from ", fileName)
    oldData = pd.read_csv(fileName)
    newData = parse_pathTrains(1)
    saturday = dfc.find_saturday_dates_strings(1)
    totalData = pd.concat([oldData, newData])
    totalData.sort_values(by='DATE', inplace=True)
    newName = 'pathTrains_{}_to_{}.csv'.format(fileName.split('_')[1], saturday[0])
    print("Trying to write data to ", newName)
    totalData.to_csv(newName)


def parse_pathTrains(number):
    df = dfc.get_n_latest_mta_dataframes(number)
    path = dfc.pathRidesPerDay(df)
    path = dfm.modify_for_outliers(path)
    path = dfm.sum_lists_in_rows(path)
    return path


def parse_pathTrains_to_csv(number):
    path = parse_pathTrains(number)
    saturdays = dfc.find_saturday_dates_strings(number)
    fileName = 'pathTrains_{}_to_{}.csv'.format(saturdays[-1], saturdays[0])
    print('Attempting to write to file: ', fileName)
    path.to_csv(fileName)


def parse_non_path_trains_to_csv(number):
    trains = parse_non_path_trains(number)
    saturdays = dfc.find_saturday_dates_strings(number)
    fileName = 'data/nonPathTrains_{}_to_{}.csv'.format(saturdays[-1], saturdays[0])
    print('Attempting to write to file: ', fileName)
    trains.to_csv(fileName)


def parse_non_path_trains(number):
    df = dfc.get_n_latest_mta_dataframes(number)
    trains = dfc.rides_per_day(df)
    trains = dfm.modify_for_outliers(trains)
    trains = dfm.sum_lists_in_rows(trains)
    return trains


def sort_by_date(df, fileName):
    df.sort_values(by='DATE', inplace=True)
    df.to_csv(fileName)


def analyze_n_dataframes_by_DBSCAN(number):
    data = dfc.get_n_latest_mta_dataframes(number)
    saturdays = dfc.find_saturday_dates_strings(number)
    data = data[data['DESC'] == 'REGULAR']
    analyzedData = ag.analyze(data)
    print(ag.count_negative_groups(analyzedData))
    analyzedData.to_csv('data/dbscan_analysis_{}_to_{}.csv'.format(saturdays[-1], saturdays[0]))


def analyze_latest_dataframe_by_DBSCAN_():
    data = dfc.get_latest_mta_dataframe()
    saturday = dfc.find_last_saturday_string()
    data = data[data['DESCRIPTION'] == 'REGULAR']
    analyzedData = ag.analyze(data)
    analyzedData.to_csv('data/dbscan_analysis_{}.csv'.format(saturday))


def analyze_latest_dataframe_by_DBSCAN(station):
    data = dfc.get_latest_mta_dataframe()
    saturday = dfc.find_last_saturday_string()
    data = data[data['STATION'] == station]
    analyzedData = ag.analyze(data)
    analyzedData.to_csv('data/dbscan_analysis_of_{}_{}.csv'.format(station, saturday))
