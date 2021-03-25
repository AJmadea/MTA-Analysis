import pandas as pd
from datetime import datetime, timedelta
from urllib.error import HTTPError
import plotly.express as px
import numpy as np
import DataframeCreation as dfc
import DataframeModification as dfm
import Graphs as g

if __name__ == '__main__':
    pathTrains = pd.read_csv('data/past_ten_dataframes_210109_to_210320.csv')
    print(pathTrains.shape)
    g.graph_scatter(pathTrains)
    pathTrains = dfm.get_isodate_number(pathTrains)
    pathTrains.drop('Unnamed: 0', axis=1, inplace=True)
    print(pathTrains.head())