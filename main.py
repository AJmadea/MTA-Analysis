import pandas as pd
from datetime import datetime, timedelta
from urllib.error import HTTPError
import plotly.express as px
import numpy as np
import DataframeCreation as dfc
import DataframeModification as dfm
import Graphs as g
import CSVFile as f

if __name__ == '__main__':
    path = pd.read_csv('pathTrains_210102_to_210320.csv')
    weekdays, weekends = dfm.weekend_dependent_split(path)

    g.graph_scatter(df=weekdays, title="Weekdays Entries v.s. Exits")
    g.graph_scatter(df=weekends, title="Weekends Entries v.s. Exits")
