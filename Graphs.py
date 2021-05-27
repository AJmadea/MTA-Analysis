import plotly.express as px
import plotly.graph_objs as go
import DataframeModification as dfm
import Statistics as s


def graph_over_time(data):
    if 'RIDERSHIP' in data.columns:
        rider_fig = px.line(data, x='DATE', y='RIDERSHIP', title='Ridership Over Time')
        rider_fig.show()

    entry_fig = px.line(data, x='DATE', y='ENTRIES', title='Entries Over Time')
    exit_fig = px.line(data, x='DATE', y='EXITS', title='Exits Over Time')

    entry_fig.show()
    exit_fig.show()


def graph_certain_stations(data, certainStations):
    print('Filtering rows in the dataframe')
    print(data.shape)

    data = data[(data['DATE'] == '03/02/2020') |
                (data['DATE'] == '03/19/2020') |
                (data['DATE'] == '04/01/2020')]

    for i in data.index:
        if data.loc[i, 'STATION'] not in certainStations:
            data.drop(index=i, axis=0, inplace=True)

    data.to_csv('data_by_date/data_in_certainStations.csv')

    print('Calculating the x and y ranges...')
    range_x = [-10, data['EXITS'].max() * 1.2]
    range_y = [-10, data['ENTRIES'].max() * 1.2]

    print('Creating the figure...')
    fig = px.scatter(data, x='EXITS', y='ENTRIES', animation_frame='DATE', title='COVID19 affected Stations',
                     color='STATION', range_x=range_x, range_y=range_y)
    fig.show()


def graph_scatter_rides_over_time(data):
    #data.sort_values(by='DATE', inplace=True)
    fig = px.scatter(data, x='EXITS', y='ENTRIES', animation_frame='DATE', color='STATION', title='Rides Over Time',
                     range_x=[-10, 50000], range_y=[-10, 50000])
    fig.show()


def graph_entries_v_exits(df):
    graph_entries_v_exits(df=df, title='Entries v.s. Exits for Stations')


def graph_entries_v_exits(df, title):
    if 'ISOWEEKDAY' not in df.columns:
        df = dfm.get_isodate_number(df)

    fig = px.scatter(df, x='EXITS', y='ENTRIES', color='STATION',
                     title=title)

    print("About to show the chart...")
    fig.show()


def graph_pathTrains_over_time(pathTrains):
    pathGroupedEntries = pathTrains.groupby(['STATION', 'DATE'])['ENTRIES'].sum().reset_index()
    pathGroupedExits = pathTrains.groupby(['STATION', 'DATE'])['EXITS'].sum().reset_index()

    figs = [px.line(pathGroupedEntries, x='DATE', y='ENTRIES', color='STATION', title='ENTRIES for the PATH Train'),
            px.line(pathGroupedExits, x='DATE', y='EXITS', color='STATION', title='Exits for the PATH')]

    for f in figs:
        f.show()


def graph_entry_to_exit_ratio_overtime(df):
    if 'ENTRIES/EXITS' not in df.columns:
        df = dfm.entry_exit_ratio(df)
    df.sort_values(by='DATE', inplace=True)
    fig = px.line(df, x='DATE', y='ENTRIES/EXITS', color='STATION', title='Entry To Exit Ratio Over Time')
    fig.show()
