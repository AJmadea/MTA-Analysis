import ibm_db
import DataframeModification as dfm
import pandas as pd
import plotly.express as px


def read_credentials():
    lines = None
    with open("C:/Users/Andrew/Desktop/pythonMTAanalysis/database_credentials.txt", "r") as f:
        lines = f.read().split("|")
    return lines[0], lines[1], lines[2]


def format_sql(data):
    diction = dfm.create_date_dictionary_string(data)
    base_sql = "INSERT INTO RIDES_OVER_TIME(DATE_RECORD, ENTRIES, EXITS) VALUES "
    for i in data.index:
        date = diction[data.loc[i, 'DATE']]
        entry = data.loc[i, 'ENTRIES']
        exits = data.loc[i, 'EXITS']
        append = "(\'{}\',{},{}),".format(date, int(entry), int(exits))
        base_sql = base_sql + append
    return base_sql


def connect_execute_rides_over_time(data):
    sql_statement = format_sql(data)[:-1] # [:-1] to get rid of the last comma in the entry
    print(sql_statement)
    _dsn, _uid, _pwd = read_credentials()
    conn = ibm_db.connect(_dsn, _uid, _pwd)
    ibm_db.exec_immediate(conn, sql_statement)
    ibm_db.close(conn)


def get_station_rides(dsn, user, pwd, station ):
    dsn, user, pwd = read_credentials()
    # Connecting to DB2
    conn = ibm_db.connect(dsn, user, pwd)

    # Sending SQL command
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

    return data


def get_rides_over_time():
    # Creating credentials
    dsn, user, pwd = read_credentials()

    # Connecting to DB2
    conn = ibm_db.connect(dsn, user, pwd)

    # Sending SQL command
    result = ibm_db.exec_immediate(conn, "SELECT DATE_RECORD,ENTRIES,EXITS FROM RIDES_OVER_TIME")

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
    print(data.head())
    return data


def create_graphs_over_time():
    data = get_rides_over_time()
    for i in data.index:
        data.loc[i, 'WEEKDAY'] = "Yes" if data.loc[i, 'DATE'].isoweekday() < 6 else "No"
    weekday_data = data[data['WEEKDAY'] == 'Yes']
    weekend_data = data[data['WEEKDAY'] == "No"]

    weekend_entry_fig = px.line(weekend_data, x='DATE', y='ENTRIES', title='Weekend Entries')
    weekend_entry_fig.show()

    weekday_entry_fig = px.line(weekday_data, x="DATE", y='ENTRIES', title='Weekday Entries')
    weekday_entry_fig.show()

    #entries_fig = px.line(data, x='DATE', y='ENTRIES', title='Entries Over Time MTA')
    #exit_fig = px.line(data, x='DATE', y='EXITS', title='Exits Over Time MTA')
