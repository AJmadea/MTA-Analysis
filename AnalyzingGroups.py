from sklearn.cluster import DBSCAN
import pandas as pd


def analyze(df):
    final = pd.DataFrame(data={}, columns=['STATION', 'DATE', 'ENTRIES', 'EXITS'])
    db = DBSCAN(eps=1000, min_samples=2)

    for station in df['STATION'].unique():
        for date in df['DATE'].unique():
            f = df[(df['STATION'] == station) & (df['DATE'] == date)]
            db.fit(f[['ENTRIES', 'EXITS']])
            f['LABELS'] = db.labels_

            entries = 0
            exits = 0
            for label in f['LABELS'].unique():
                temp = f[f['LABELS'] == label]

                entryList = temp['ENTRIES'].tolist()
                exitList = temp['EXITS'].tolist()

                entries = entryList[-1] - entryList[0] + entries
                exits = exitList[-1] - exitList[0] + exits
            final = final.append(other={'STATION': f['STATION'].unique().tolist()[0],
                                        'DATE': f['DATE'].unique().tolist()[0],
                                        'ENTRIES': entries,
                                        'EXITS': exits
                                        }, ignore_index=True)
        return final
