import pandas as pd
import ibm_db
import plotly.express as px
from datetime import date
import streamlit as st


@st.cache(hash_funcs={ibm_db.IBM_DBConnection: lambda _: None})
def get_ride_data(_conn):
    result = ibm_db.exec_immediate(_conn, "SELECT DATE_RECORD,ENTRIES,EXITS FROM RIDES_OVER_TIME")

    # Creating empty lists for dataframe
    dates = []
    entries = []
    exits = []

    # Parsing info from db2 into pandas dataframe
    row = ibm_db.fetch_tuple(result)
    while row:
        dates.append(row[0])
        entries.append(row[1])
        exits.append(row[2])
        row = ibm_db.fetch_tuple(result)
    ibm_db.close(_conn)

    _data = pd.DataFrame(data={'DATE': dates, 'ENTRIES': entries, 'EXITS': exits})
    _data.sort_values(by='DATE', inplace=True)
    return _data


@st.cache(hash_funcs={ibm_db.IBM_DBConnection: lambda _: None})
def get_station_data(conn, station):

    result = ibm_db.exec_immediate(conn, "SELECT DATE_,ENTRIES,EXITS FROM RIDES_PER_STATION WHERE STATION = \'"
                                   + station + "\'")
    
    # Creating empty lists for dataframe
    dates = []
    entries = []
    exits = []

    # Parsing info from db2 into pandas dataframe
    row = ibm_db.fetch_tuple(result)
    while row:
        dates.append(row[0])
        entries.append(row[1])
        exits.append(row[2])
        row = ibm_db.fetch_tuple(result)
    ibm_db.close(conn)

    data = pd.DataFrame(data={'DATE': dates, 'ENTRIES': entries, 'EXITS': exits})

    pandemic_date = date(2020, 3, 13)
    for i in data.index:
        current = data.loc[i, 'DATE']
        data.loc[i, 'WEEKDAY'] = 'WEEKDAY' if current.isoweekday() < 6 else 'WEEKEND'
        data.loc[i, 'PANDEMIC'] = 'PRE' if current <= pandemic_date else "POST"

    data.sort_values(by='DATE', inplace=True)
    return data


@st.cache(hash_funcs={ibm_db.IBM_DBConnection: lambda _: None})
def get_all_stations(_conn):
    all_stations = []
    result = ibm_db.exec_immediate(_conn, "SELECT DISTINCT(STATION) FROM RIDES_PER_STATION")

    row = ibm_db.fetch_tuple(result)
    while row:
        all_stations.append(row[0])
        row = ibm_db.fetch_tuple(result)
    ibm_db.close(_conn)
    return all_stations


def get_boxplot(data, choice, station):
    #print(data.describe())
    pandemic_date = date(2020, 3, 13)
    for i in data.index:
        current = data.loc[i, 'DATE']
        data.loc[i, 'WEEKDAY'] = 'WEEKDAY' if current.isoweekday() < 6 else 'WEEKEND'
        data.loc[i, 'PANDEMIC'] = 'PRE' if current <= pandemic_date else "POST"

    return px.box(data, x='PANDEMIC', y=choice, title="BoxPlot {} for {}".format(choice, station))


def get_connection():
    return ibm_db.pconnect(st.secrets['dsn'], st.secrets['user'], st.secrets['pws'])


if __name__ == '__main__':

    graph_type = st.selectbox(label="What To Graph", options=
        ("Station Rides", "Entries/Exits Scatter Plot", "Rides Over Time"))

    if graph_type == "Rides Over Time":
        choice = st.radio(label='', options=("Plot The Entries", "Plot the Exits"))
        data = get_ride_data(get_connection())
        choice = choice.split(" ")[2].upper()
        fig = px.line(data, x="DATE", y=choice, title=choice+" Over Time")
        st.plotly_chart(fig)
    else:
        stations = get_all_stations(get_connection())
        penn_sta = stations.index('34 ST-PENN STA')
        station = st.selectbox(label="Select A Station", options=stations, index=penn_sta)
        data = get_station_data(get_connection(), station)

        if graph_type == "Entries/Exits Scatter Plot":
            fig = px.scatter(data, x='EXITS', y='ENTRIES', color='PANDEMIC', symbol="WEEKDAY",
                             title="Scatter Plot of Entries V.S. Exits for "+station)
            st.plotly_chart(fig)
        elif graph_type == "Station Rides":
            choice = st.radio(label="", options=("Plot The Entries", "Plot the Exits"))
            choice = choice.split(" ")[2].upper()
            fig = px.line(data, x="DATE", y=choice, title=choice+" Over Time for "+station)
            st.plotly_chart(fig)
            # Use data to get the average and quartiles.
            st.plotly_chart(get_boxplot(data, choice, station))