import DataframeCreation as dfc
import DataframeModification as dfm
import pandas as pd


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
