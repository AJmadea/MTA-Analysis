import ibm_db
import DataframeModification as dfm


def read_credentials():
    lines = None
    with open("database_credentials.txt", "r") as f:
        lines = f.readlines().split("|")
    return lines[0], lines[1], lines[2]


def format_sql(data):
    diction = dfm.create_date_dictionary_string(data)
    base_sql = "INSERT INTO RIDES_OVER_TIME(DATE_RECORD, ENTRIES, EXITS) VALUES "
    for i in data.index:
        date = diction[data.loc[i,'DATE']]
        entry = data.loc[i, 'ENTRIES']
        exits = data.loc[i, 'EXITS']
        append = "(\'{}\',{},{}),".format(date, int(entry), int(exits))
        base_sql = base_sql + append
    return base_sql


def connect_execute(data):
    sql_statement = format_sql(data)[:-1] # [:-1] to get rid of the last comma in the entry
    _dsn, _uid, _pwd = read_credentials()
    conn = ibm_db.connect(_dsn, _uid, _pwd)

    ibm_db.exec_immediate(conn, sql_statement)
    ibm_db.close(conn)

