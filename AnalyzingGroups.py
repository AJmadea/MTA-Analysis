from sklearn.cluster import DBSCAN
import pandas as pd
import numpy as np

def analyze(df):
    final = pd.DataFrame(data={}, columns=['STATION', 'DATE', 'ENTRIES', 'EXITS'])
    db = DBSCAN(eps=1000, min_samples=2)
    print('Number of iterations: ', df['STATION'].nunique() * df['DATE'].nunique())

    outlierCounter = 0
    for station in df['STATION'].unique():
        for date in df['DATE'].unique():
            print(station, ' ', date)
            f = df[(df['STATION'] == station) & (df['DATE'] == date)]

            if f[['ENTRIES', 'EXITS']].shape[0] == 0:
                continue

            db.fit(f[['ENTRIES', 'EXITS']])

            labelList = db.labels_.tolist()
            f['LABELS'] = db.labels_

            entries = 0
            exits = 0
            for label in f['LABELS'].unique():
                if label == -1:
                    outlierCounter=outlierCounter+1
                    continue
                temp = f[f['LABELS'] == label]

                entryList = temp['ENTRIES'].tolist()
                exitList = temp['EXITS'].tolist()

                if len(entryList) > 0:
                    entries = abs(entryList[-1] - entryList[0]) + entries
                if len(exitList) > 0:
                    exits = abs(exitList[-1] - exitList[0]) + exits
            final = final.append(other={'STATION': f['STATION'].unique().tolist()[0],
                                        'DATE': f['DATE'].unique().tolist()[0],
                                        'ENTRIES': entries,
                                        'EXITS': exits
                                        }, ignore_index=True)
            f.drop('LABELS', axis=1, inplace=True)
    print('# of outliers ', outlierCounter)
    return final


def count_negative_groups(data):
    negativeEntriesDf = data[data['ENTRIES'] < 0]
    negativeExitsDf = data[data['EXITS'] < 0]

    return '{} Entries & {} Exits are negative'.format(len(negativeEntriesDf),
                                                       len(negativeExitsDf))
