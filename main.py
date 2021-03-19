import pandas as pd
from datetime import datetime, timedelta
import matplotlib as plt
from urllib.error import HTTPError
'''
@ returns the date of the last saturday
'''
def findLastSaturdayDate():
    saturday = None
    today = datetime.today().date()
    day = today.isoweekday()

    # Ternary Operator to choose the previous saturday
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
        return df
    except HTTPError as err:
        date_str = (findLastSaturdayDate()-timedelta(days=-7)).isoformat().replace('-', '')[2:]
        baseURL = "http://web.mta.info/developers/data/nyct/turnstile/turnstile_{}.txt".format(date_str)
        df = pd.read_csv(baseURL)
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

    l = [0,10,0,200]
    print(find_differences(l)) # Prints out 210

    '''
    The errorColumn is known as 'EXITS              
    It has a lot of spaces at the end of the string which makes the call
    df['EXITS'] or the like like invalid.  These two lines fix column label as 'EXITS'
    '''
    errorColumn = df.columns[df.columns.size-1]
    df.rename({errorColumn: 'EXITS'}, axis=1, inplace=True)

    # Just screwing around with this part.  Getting the times the MTA updates their info.
    # Getting the hour position and converting it to an int
    df['TIME'] = df['TIME'].str.slice(0, 2)
    df[['TIME']] = df['TIME'].astype('int')

    print('Data Types: ', df.dtypes)
    print('Shape: ', df.shape)

    # Creating histogram
    df['TIME'].plot(kind="hist", xlabel='Frequency',ylabel='Hour of the day',title='Frequency of Hour of MTA Reporting')

    plt.pyplot.show()