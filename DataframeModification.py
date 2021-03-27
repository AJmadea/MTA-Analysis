import numpy as np
from datetime import date as dt


def create_date_dictionary(df):
    d = {}
    dates = df['DATE'].unique()
    for date in dates:
        string = '{}-{}-{}'.format(date[6:], date[0:2], date[3:5])
        d.__setitem__(date, dt.fromisoformat(string))
    return d


def add_date_related_columns(df):
    d = create_date_dictionary(df)

    for i in df.index:
        newDate = d.get(df.loc[i, 'DATE'])
        df.loc[i, 'ISOWEEKDAY'] = newDate.isoweekday()
        df.loc[i, 'MONTH'] = newDate.month
        df.loc[i, 'DAY'] = newDate.day
        df.loc[i, 'YEAR'] = newDate.year


def drop_weekends(df):
    if 'ISOWEEKDAY' not in df.columns:
        df = get_isodate_number(df)

    return df[df['ISOWEEKDAY'] >= 6]


def drop_weekdays(df):
    if 'ISOWEEKDAY' not in df.columns:
        df = get_isodate_number(df)

    return df[df['ISOWEEKDAY'] < 6]


def weekend_dependent_split(df):
    frames = []

    weekends = df[df['ISODATE'] >= 6]
    weekdays = df[df['ISODATE'] < 6]

    frames.append(weekdays)
    frames.append(weekends)
    return frames


def get_isodate_number(df):
    #                       0123456789
    # create dictionary of 'MM/DD/YYYY' KEY to YYYY-MM-DD VALUE
    dates = df['DATE'].unique()
    d = {}
    for date in dates:
        string = '{}-{}-{}'.format(date[6:], date[0:2], date[3:5])
        d.__setitem__(date, dt.fromisoformat(string).isoweekday())

    for i in df.index:
        df.loc[i, 'ISOWEEKDAY'] = d.get(df.loc[i, 'DATE'])

    return df


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

