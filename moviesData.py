import streamlit as st
import pandas as pd
import plotly.express as px


def read_data():
    dataframe = pd.read_csv("data source\\movies data 2.csv")
    pd.set_option('max_columns', 11)
    return dataframe


def sidebar():
    dataframe = read_data()
    data = dataframe.groupby(dataframe['actorName'])
    actor = []
    for i, j in data:
        actor.append(i)
    select = st.sidebar.selectbox("Select a Actor", actor, index=0)
    show_actor_data(select, data)


def show_actor_data(select, data):
    actor_data = pd.DataFrame([])
    for i, j in data:
        if i == select:
            actor_data = j
    actor_birth = int(actor_data['birthYear'].max())
    actor_death = actor_data['deathYear'].isnull().any()
    st.write(f'''
                {select}

                Birth Year:{actor_birth}
                ''')
    if not actor_death:
        st.write(f"Death Year:{int(actor_data['deathYear'].max())}")
    actor_data = actor_data.drop(['actorName', 'deathYear', 'birthYear'], axis=1)
    actor_data['MovieId']=[i for i in range(1,len(actor_data.index)+1)]
    actor_data = actor_data.set_index('MovieId')
    st.write(actor_data)
    col1,col2,col3 = st.columns(3)
    col1.plotly_chart(px.bar(actor_data, x=actor_data.index, y='averageRating', color='averageRating'))



st.header("*Actor*")
sidebar()



