import pandas as pd
from datetime import datetime, timedelta
import matplotlib as plt
from urllib.error import HTTPError
import plotly.express as px
import numpy as np

import DataframeCreation as dfc

def find_differences(dlist):
    if len(dlist) <= 1:
        return 0

    diff = 0
    t = [dlist[0]]
    for n in range(0, len(dlist)):
        if t[-1] <= dlist[n]:
            t.append(dlist[n])
        else:
            diff = diff + t[-1] - t[0]
            t.clear()
            t.append(dlist[n])
    if len(t) == 1:
        diff = diff + t[0]
    else:
        diff = diff + t[-1] - t[0]
    return diff

def modify_for_outliers(dataframe):
    # Create a STD column for Entries, Exits

    for i in dataframe.index:
        dataframe.loc[i, 'ENTRIES STD'] = np.asarray(dataframe.loc[i, 'ENTRIES']).std()
        dataframe.loc[i, 'EXITS STD'] = np.asarray(dataframe.loc[i, 'EXITS']).std()

    for i in dataframe.index:
        if dataframe.loc[i, 'EXITS STD'] > 2000:
            print(dataframe.loc[i, ])
            arr = np.asarray(dataframe.loc[i, 'EXITS'])
            arr.sort()
            arr[-1] = 0
            dataframe.loc[i, 'EXITS'] = arr.sum()
        if dataframe.loc[i, 'ENTRIES STD'] > 2000:
            print(dataframe.loc[i, ])
            arr = np.asarray(dataframe.loc[i, 'ENTRIES'])
            arr.sort()
            arr[-1] = 0
            dataframe.loc[i, 'ENTRIES'] = arr.sum()

    dataframe.drop(['ENTRIES STD', 'EXITS STD'], axis=1, inplace=True)
    return dataframe

def sum_lists_in_rows(dataframe):
    for i in dataframe.index:
        dataframe.loc[i, 'ENTRIES'] = np.asarray(dataframe.loc[i, 'ENTRIES']).sum()
        dataframe.loc[i, 'EXITS'] = np.asarray(dataframe.loc[i, 'EXITS']).sum()
    return dataframe

if __name__ == '__main__':

    df = dfc.get_n_latest_mta_dataframes(10)
    print(df.shape)

    #df = get_latest_mta_dataframe()
    pathTrains = dfc.pathRidesPerDay(df)
    pathTrains = modify_for_outliers(pathTrains)
    pathTrains = sum_lists_in_rows(pathTrains)

    pathTrains.to_csv('past_ten_dataframes_210109_to_210320.csv')

    pathGroupedEntries = pathTrains.groupby(['STATION', 'DATE'])['ENTRIES'].sum().reset_index()
    pathGroupedExits = pathTrains.groupby(['STATION', 'DATE'])['EXITS'].sum().reset_index()

    figs = [px.line(pathGroupedEntries, x='DATE', y='ENTRIES', color='STATION', title='ENTRIES for the PATH Train'),
            px.line(pathGroupedExits, x='DATE', y='EXITS', color='STATION', title='Exits for the PATH')]

    for f in figs:
        f.show()

    print('Data Types: ', df.dtypes)
    print('Shape: ', df.shape)
