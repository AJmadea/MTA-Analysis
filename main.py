import pandas as pd
from datetime import datetime, timedelta
import matplotlib as plt

'''
@ returns the date of the last saturday
'''
def findLastSaturdayDate():
    saturday = None
    today = datetime.today().date()
    day = today.isoweekday()
    if day == 6:
        saturday = today
    elif day == 7:  # Today is Sunday.  Sunday is 7.  Sunday - 1 is saturday
        saturday = today - timedelta(days=1)
    else:
        saturday = today - timedelta(days=(day+1))
    return saturday.isoformat().replace('-', '')[2:]

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
                entries = entries + (entryList[len(entryList) - 1] - entryList[0])
                exits = exits + (exitList[len(exitList) - 1] - exitList[0])

        final = final.append(other={'DATE': date,
                                    'STATION': station,
                                    'ENTRIES': entries,
                                    'EXITS': exits
                                    }, ignore_index=True)

if __name__ == '__main__':
    dateString = findLastSaturdayDate()
    print('Date To be used: ', dateString)
    baseURL = "http://web.mta.info/developers/data/nyct/turnstile/turnstile_{}.txt".format(dateString)
    df = pd.read_csv(baseURL)

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