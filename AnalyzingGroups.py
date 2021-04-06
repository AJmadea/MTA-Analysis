from sklearn.cluster import DBSCAN
import pandas as pd


def analyze(df):
    final = pd.DataFrame(data={}, columns=['STATION', 'DATE', 'ENTRIES', 'EXITS'])
    db = DBSCAN(eps=1000, min_samples=2)
    print(df['STATION'].nunique() * df['DATE'].nunique())

    for station in df['STATION'].unique():
        for date in df['DATE'].unique():
            f = df[(df['STATION'] == station) & (df['DATE'] == date)]
            db.fit(f[['ENTRIES', 'EXITS']])

            labelList = db.labels_.tolist()
            f['LABELS'] = db.labels_

            entries = 0
            exits = 0
            for label in f['LABELS'].unique():
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

    return final


def count_negative_groups(data):
    negativeEntries = 0
    negativeExits = 0
    for i in data.index:
        if data.loc[i, 'ENTRIES'] < 0:
            negativeEntries = negativeEntries + 1
        if data.loc[i, 'EXITS'] < 0:
            negativeExits = negativeExits + 1

    return '{} Entries & {} Exits are negative'.format(negativeEntries, negativeExits)