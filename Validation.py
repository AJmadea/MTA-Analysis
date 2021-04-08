import pandas as pd
import numpy as np


def create_dataframe_error(data):
    # Getting data from file.
    validationCSV = 'data/MTA_recent_ridership_data_20210406.csv'
    validation = pd.read_csv(validationCSV)

    # Cleaning up column names and dropping unwanted columns
    validation.rename({'Subways: Total Estimated Ridership': 'CORRECT TOTAL'}, axis=1, inplace=True)
    validation.rename({'Date': 'DATE'}, axis=1, inplace=True)
    validation.drop(validation.columns[2:], axis=1, inplace=True)

    # Correcting the date format from M/D/YYYY to MM/DD/YYYY
    validDates = validation['DATE'].unique()
    validDates = correct_format(validDates)

    # Finding intersection of the dates
    validation['DATE'] = validDates
    dataDates = data['DATE'].unique()
    dateIntersection = np.intersect1d(validDates, dataDates)

    # Dropping rows in the validation frame that do not have a valid date
    for i in validation.index:
        if validation.loc[i, 'DATE'] not in dateIntersection:
            validation.drop(index=i, axis=0, inplace=True)

    # sorting values by date.  Resetting index
    validation.sort_values(by='DATE', inplace=True)
    data.sort_values(by='DATE', inplace=True)
    validation.reset_index(inplace=True)
    data.reset_index(inplace=True)

    # Setting index to date to ensure the right values are assigned.
    validation.set_index(keys='DATE', inplace=True)
    data.set_index(keys='DATE', inplace=True)

    # Assigning estimated entry/exit values to the correct date
    for date in dateIntersection:
        validation.loc[date, 'DBSCAN ENTRY'] = data.loc[date, 'ENTRIES']
        validation.loc[date, 'DBSCAN EXITS'] = data.loc[date, 'EXITS']

    validation['ENTRY ERROR'] = (validation['DBSCAN ENTRY'] - validation['CORRECT TOTAL']) / validation['CORRECT TOTAL'] * 100
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
