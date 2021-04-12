import plotly.express as px
import DataframeModification as dfm


def graph_rides_over_time(data):
    data.sort_values(by='DATE', inplace=True)
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
