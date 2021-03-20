import pandas as pd
from datetime import datetime, timedelta
import matplotlib as plt
from urllib.error import HTTPError
import plotly.express as px

'''
@ returns the date of the last saturday
'''
def findLastSaturdayDate():
    saturday = None
    today = datetime.today().date()
    day = today.isoweekday()

    # Ternary Operator to choose the previous saturday
    # -(day % 6 + 1) changes isoformat for each day to the previous saturday
    saturday = today if day == 6 else today + timedelta(days=-(day % 6 + 1))
    return saturday

def pathRidesPerDay(dataframe):
    final = pd.DataFrame(data={}, columns=['DATE', 'STATION', 'ENTRIES', 'EXITS'])
    dataframe = dataframe[dataframe['DIVISION']=='PTH']
    for date in dataframe['DATE'].unique():
        for station in dataframe['STATION'].unique():
            entries = 0
            exits = 0
            for scp in dataframe['SCP'].unique():
                temp = dataframe[(dataframe['DATE'] == date) & (dataframe['STATION'] == station) & (dataframe['SCP'] == scp)]
                if len(temp) != 0:
                    entryList = temp['ENTRIES'].to_list()
                    exitList = temp['EXITS'].to_list()
                    entries = entries + find_differences(entryList)
                    exits = exits + find_differences(exitList)

            final = final.append(other={'DATE': date,
                                        'STATION': station,
                                        'ENTRIES': entries,
                                        'EXITS': exits
                                        }, ignore_index=True)

    return final

def get_mta_dataframe():
    dateString = findLastSaturdayDate().isoformat().replace('-', '')[2:]
    print('Date To be used: ', dateString)
    try:
        baseURL = "http://web.mta.info/developers/data/nyct/turnstile/turnstile_{}.txt".format(dateString)
        df = pd.read_csv(baseURL)
    except HTTPError as err:
        date_str = (findLastSaturdayDate()-timedelta(days=-7)).isoformat().replace('-', '')[2:]
        baseURL = "http://web.mta.info/developers/data/nyct/turnstile/turnstile_{}.txt".format(date_str)
        df = pd.read_csv(baseURL)
    finally:
        # The last column is supposed to be 'EXITS' but it has alot of spaces after it right now
        errorColumn = df.columns[-1]
        df.rename({errorColumn: 'EXITS'}, axis=1, inplace=True)
        return df


def find_differences(dlist):

    diff = 0
    t = []
    tCounter = 0
    for n in range(0, len(dlist)):
        if len(t) == 0:
            t.append(dlist[n])
        else:
            tCounter = tCounter + 1
            if t[tCounter - 1] <= dlist[n]:
                t.append(dlist[n])
            else:
                diff = diff + t[-1] - t[0]
                tCounter = 0
                t.clear()
                t.append(dlist[n])
    if len(t) == 1:
        diff = diff + t[0]
    else:
        diff = diff + t[-1] - t[0]
    return diff

if __name__ == '__main__':

    df = get_mta_dataframe()
    pathTrains = pathRidesPerDay(df)
    pathGroupedEntries = pathTrains.groupby(['STATION', 'DATE'])['ENTRIES'].sum().reset_index()
    pathGroupedExits = pathTrains.groupby(['STATION', 'DATE'])['EXITS'].sum().reset_index()

    figs = [px.line(pathGroupedEntries, x='DATE', y='ENTRIES', color='STATION', title='ENTRIES for the PATH Train'),
            px.line(pathGroupedExits, x='DATE', y='EXITS', color='STATION', title='Exits for the PATH')]

    for f in figs:
        f.show()

    print('Data Types: ', df.dtypes)
    print('Shape: ', df.shape)

