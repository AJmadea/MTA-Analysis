from sklearn.cluster import DBSCAN
from sklearn.cluster import OPTICS
import warnings
import pandas as pd


def analyze_optics(df, max_eps):
    warnings.filterwarnings('ignore')
    final = pd.DataFrame(data={}, columns=['STATION', 'DATE', 'ENTRIES', 'EXITS'])
    db = OPTICS(max_eps=max_eps, min_cluster_size=2)
    print('Number of iterations: ', df['STATION'].nunique() * df['DATE'].nunique())

    outlierCounter = 0
    for station in df['STATION'].unique():
        print('Currently fitting: ', station)
        for date in df['DATE'].unique():
            f = df[(df['STATION'] == station) & (df['DATE'] == date)]

            if f[['ENTRIES', 'EXITS']].shape[0] == 0:
                continue

            db.fit(f[['ENTRIES', 'EXITS']])

            f['LABELS'] = db.labels_

            entries = 0
            exits = 0
            for label in f['LABELS'].unique():
                if label == -1:
                    outlierCounter = outlierCounter + 1
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


def analyze(df, eps, min_samples):
    warnings.filterwarnings('ignore')
    final = pd.DataFrame(data={}, columns=['STATION', 'DATE', 'ENTRIES', 'EXITS'])
    db = DBSCAN(eps=eps, min_samples=min_samples)
    print('Number of iterations: ', df['STATION'].nunique() * df['DATE'].nunique())

    outlierCounter = 0
    for station in df['STATION'].unique():
        print('Currently fitting: ', station)
        for date in df['DATE'].unique():
            f = df[(df['STATION'] == station) & (df['DATE'] == date)]

            if f[['ENTRIES', 'EXITS']].shape[0] == 0:
                continue

            db.fit(f[['ENTRIES', 'EXITS']])
            f['LABELS'] = db.labels_

            entries = 0
            exits = 0
            for label in f['LABELS'].unique():
                if label == -1:
                    outlierCounter += 1
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

