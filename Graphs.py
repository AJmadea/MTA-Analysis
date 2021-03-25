import plotly.express as px
import DataframeModification as dfm

def graph_scatter(df):

    df = dfm.get_isodate_number(df)
    fig = px.scatter(df, x='ENTRIES', y='EXITS', color='STATION',
                     symbol='ISODATE NUMBER', title='Entries v.s. Exits for PATH Stations')

    fig.show()

def graph_pathTrains_over_time(pathTrains):
    pathGroupedEntries = pathTrains.groupby(['STATION', 'DATE'])['ENTRIES'].sum().reset_index()
    pathGroupedExits = pathTrains.groupby(['STATION', 'DATE'])['EXITS'].sum().reset_index()

    figs = [px.line(pathGroupedEntries, x='DATE', y='ENTRIES', color='STATION', title='ENTRIES for the PATH Train'),
            px.line(pathGroupedExits, x='DATE', y='EXITS', color='STATION', title='Exits for the PATH')]

    for f in figs:
        f.show()
