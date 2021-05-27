import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error
import plotly.express as px
import DataframeCreation as dfc
from urllib.error import HTTPError


def get_error_frame_from_file(startEPS, stopEPS, stepEPS, startSample, stopSample, fromDate, toDate, ):
    fromDate = dfc.get_last_saturday_string_from_date(fromDate)
    toDate = dfc.get_last_saturday_string_from_date(toDate)
    fileName = 'data/error_dataframes/error_dataframe_eps=[{},{}]_min_samples=[{},{}]_from_{}_to_{}.csv'. \
        format(startEPS, stopEPS - stepEPS, startSample, stopSample - 1, fromDate, toDate)

    data = pd.read_csv(fileName)
    return data


def graph_all_errors_3D(startEPS, stopEPS, stepEPS, startSample, stopSample, fromDate, toDate):
    errors = ['R2', 'MSE', 'MAE']
    attrTypes = ['ENTRIES', 'EXITS']
    for e in errors:
        for a in attrTypes:
            graph_errors(startEPS, stopEPS, stepEPS, startSample, stopSample, fromDate, toDate,
                         '{} {}'.format(e, a))


def graph_errors(startEPS, stopEPS, stepEPS, startSample, stopSample, fromDate, toDate, whatToGraph):
    data = get_error_frame_from_file(startEPS, stopEPS, stepEPS, startSample, stopSample, fromDate, toDate)

    if whatToGraph not in data.columns:
        whatToGraph = 'R2 ENTRIES'

    r2_graph = px.line_3d(data, x='EPS', y='MIN_SAMPLES', z=whatToGraph, title='DBSCAN Parameter Analysis: {}'.
                              format(whatToGraph))
    r2_graph.show()


def get_correct_values(dates):
    # Getting data from file.
    try:
        validationCSV = 'http://new.mta.info/document/20441'
        validation = pd.read_csv(validationCSV)
    except HTTPError as err:
        err.print()
        print("Something happened when trying to get the info from new.mta.info")
        print('Will attempt to read it locally...')
        validation = pd.read_csv('data/MTA_recent_ridership_data_20210408.csv')

    # Cleaning up column names and dropping unwanted columns
    validation.rename({'Subways: Total Estimated Ridership': 'CORRECT TOTAL'}, axis=1, inplace=True)
    validation.rename({'Date': 'DATE'}, axis=1, inplace=True)
    validation.drop(validation.columns[2:], axis=1, inplace=True)

    validDates = validation['DATE'].unique()
    validDates = correct_format(validDates)
    validation['DATE'] = validDates

    dateIntersection = np.intersect1d(dates, validDates)

    for i in validation.index:
        if validation.loc[i, 'DATE'] not in dateIntersection:
            validation.drop(index=i, axis=0, inplace=True)

    validation.set_index(keys='DATE', inplace=True)
    validation.sort_index(inplace=True)
    return validation.reset_index()


def calculate_errors(data):
    dates = data['DATE'].unique()
    #print(dates)
    validation = get_correct_values(dates)
    print(validation.head())

    intersection = set(dates).intersection(validation['DATE'].unique())
    for i in data.index:
        if data.loc[i, 'DATE'] not in intersection:
            data.drop(index=i, axis=0, inplace=True)

    for i in validation.index:
        if validation.loc[i, 'DATE'] not in intersection:
            validation.drop(index=i, axis=0, inplace=True)

    #print(validation['DATE'].unique())

    mse = mean_squared_error(y_pred=data['ENTRIES'], y_true=validation['CORRECT TOTAL'])
    r2 = r2_score(y_pred=data['ENTRIES'], y_true=validation['CORRECT TOTAL'])
    mae = mean_absolute_error(y_pred=data['ENTRIES'], y_true=validation['CORRECT TOTAL'])

    mse_exits = mean_squared_error(y_pred=data['EXITS'], y_true=validation['CORRECT TOTAL'])
    r2_exits = r2_score(y_pred=data['EXITS'], y_true=validation['CORRECT TOTAL'])
    mae_exits = mean_absolute_error(y_pred=data['EXITS'], y_true=validation['CORRECT TOTAL'])

    mse_r = mean_squared_error(y_pred=data['RIDERSHIP'], y_true=validation["CORRECT TOTAL"])
    r2_r = r2_score(y_pred=data['RIDERSHIP'], y_true=validation["CORRECT TOTAL"])
    mae_r = mean_absolute_error(y_pred=data['RIDERSHIP'], y_true=validation["CORRECT TOTAL"])

    print('Mean Squared Error Entries: ', mse)
    print('R^2 Entries: ', r2)
    print('Mean Absolute Error Entries: ', mae)

    print('\nMean Squared Error Exits: ', mse_exits)
    print('R^2 Exits: ', r2_exits)
    print('Mean Absolute Error Exits: ', mae_exits)

    print('\nMSE Ridership:', mse_r)
    print("R2 Ridership:", r2_r)
    print("MAE Ridership:", mae_r)



def calculate_errors_for_all_dbscan(a, b, c, x, y, fromDate, toDate):
    fromDate = dfc.get_last_saturday_string_from_date(fromDate)
    toDate = dfc.get_last_saturday_string_from_date(toDate)

    fileInput = 'data/dbscan_data_outputs/dbscan_eps={}_min_samples={}_from_{}_to_{}.csv'.format(a, x, fromDate, toDate)
    data = pd.read_csv(fileInput)
    dates = data['DATE'].unique()
    errData = pd.DataFrame()

    validation = get_correct_values(dates)

    for eps in range(a, b, c):
        for min_samples in range(x, y):
            temp = 'data/dbscan_over_time/dbscan_over_time_eps={}_min_samples={}_from_{}_to_{}.csv'. \
                format(eps, min_samples, fromDate, toDate)
            data = pd.read_csv(temp, index_col='DATE')

            mse = mean_squared_error(y_pred=data['ENTRIES'], y_true=validation['CORRECT TOTAL'])
            r2 = r2_score(y_pred=data['ENTRIES'], y_true=validation['CORRECT TOTAL'])
            mae = mean_absolute_error(y_pred=data['ENTRIES'], y_true=validation['CORRECT TOTAL'])

            mse_exits = mean_squared_error(y_pred=data['EXITS'], y_true=validation['CORRECT TOTAL'])
            r2_exits = r2_score(y_pred=data['EXITS'], y_true=validation['CORRECT TOTAL'])
            mae_exits = mean_absolute_error(y_pred=data['EXITS'], y_true=validation['CORRECT TOTAL'])

            errData = errData.append(other={'EPS': eps,
                                            'MIN_SAMPLES': min_samples,
                                            'MSE ENTRIES': mse,
                                            'MSE EXITS': mse_exits,
                                            'R2 ENTRIES': r2,
                                            'R2 EXITS': r2_exits,
                                            'MAE ENTRIES': mae,
                                            'MAE EXITS': mae_exits
                                            }, ignore_index=True)

    fileOutput = 'data/error_dataframes/error_dataframe_eps=[{},{}]_min_samples=[{},{}]_from_{}_to_{}.csv'. \
        format(a, b - c, x, y - 1, fromDate, toDate)
    errData.to_csv(fileOutput)


def create_dataframe_error(dataframe):
    dataDates = dataframe['DATE'].unique()
    validation = create_dataframe_error(dataDates)
    dateIntersection = np.intersect1d(validation['DATE'].unique(), dataDates)

    # Dropping rows in the validation frame that do not have a valid date
    for i in validation.index:
        if validation.loc[i, 'DATE'] not in dateIntersection:
            validation.drop(index=i, axis=0, inplace=True)

    # sorting values by date.  Resetting index
    validation.sort_values(by='DATE', inplace=True)
    dataframe.sort_values(by='DATE', inplace=True)
    validation.reset_index(inplace=True)
    dataframe.reset_index(inplace=True)

    # Setting index to date to ensure the right values are assigned.
    validation.set_index(keys='DATE', inplace=True)
    dataframe.set_index(keys='DATE', inplace=True)

    # Assigning estimated entry/exit values to the correct date
    for date in dateIntersection:
        validation.loc[date, 'DBSCAN ENTRY'] = dataframe.loc[date, 'ENTRIES']
        validation.loc[date, 'DBSCAN EXITS'] = dataframe.loc[date, 'EXITS']

    validation['ENTRY ERROR'] = (validation['DBSCAN ENTRY'] - validation['CORRECT TOTAL']) / validation[
        'CORRECT TOTAL'] * 100
    validation['EXIT ERROR'] = (validation['DBSCAN EXITS'] - validation['CORRECT TOTAL']) / validation[
        'CORRECT TOTAL'] * 100

    validation.drop('index', axis=1, inplace=True)

    fromDate = dateIntersection[0].replace('/', '')
    toDate = dateIntersection[-1].replace('/', '')
    fileName = 'data/error_dataframe_from_{}_to_{}.csv'.format(fromDate, toDate)
    print('Saving error frame to: ', fileName)
    validation.to_csv(fileName)

    return validation


def correct_format(dates):
    newDates = []
    for date in dates:
        # M/D/YYYY
        values = date.split('/')
        if len(values[0]) == 1:
            temp = values[0]
            values[0] = ('0{}'.format(temp))

        if len(values[1]) == 1:
            temp = values[1]
            values[1] = ('0{}'.format(temp))

        newDates.append('{}/{}/{}'.format(values[0],
                                          values[1],
                                          values[2]))
    return newDates
