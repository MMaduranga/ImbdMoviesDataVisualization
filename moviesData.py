import streamlit as st
import pandas as pd


def read_data():
    dataframe = pd.read_csv("data source\\movies data.csv")
    pd.set_option('max_columns', 11)
    return dataframe


def webapp_view(*data):
    for i in data:
        st.write(i)


def sidebar():
    st.sidebar.header('SideBar')
    if st.sidebar.checkbox('Show Source Data & Details'):
        dataframe = read_data()
        webapp_view('\n\nMovies Table', dataframe, "Shape of Table", dataframe.shape, 'Columns of the table',
                    dataframe.columns)


st.header("Movies")
sidebar()




