import streamlit as st
import pandas as pd
import plotly.express as px
import requests as rq
from bs4 import BeautifulSoup as bs
import re
import streamlit.components.v1 as stc
import plotly.graph_objects as go

# Data Reading and Cleaning Part
dataframe = pd.read_csv("data source\\movies data 2.csv")
pd.set_option('max_columns', 11)
dataframe_uncleaned = dataframe
dataframe['isAdult'] = dataframe['isAdult'].replace(0, 'Not Adult')
dataframe['isAdult'] = dataframe['isAdult'].replace(1, 'Adult')
dataframe = dataframe.drop_duplicates()  # remove duplicates
dataframe = dataframe.dropna(subset=['genre'])  # remove not available values in genre
dataframe = dataframe[dataframe['runtimeMinutes'] <= 240]  # remove all values of runtime above 240  minutes
dataframe = dataframe[dataframe['runtimeMinutes'] >= 10]  # remove all values of runtime bellow 10  minutes
dataframe = dataframe[dataframe['averageRating'] >= 2]  # remove all values of averagerating bellow 2  (855 rows)
# ------------------------------------------------


def sidebar():
    data = dataframe.groupby(dataframe['actorName'])
    actor = ['']
    for i, j in data:
        actor.append(i)
    select = st.sidebar.selectbox("Select a Actor", actor, index=0)
    try:
        show_actor_data(select, data)
    except Exception:
        pass


def show_actor_data(select, data):
    actor_data = pd.DataFrame([])
    for i, j in data:
        if i == select:
            actor_data = j
            break
    actor_birth = int(actor_data['birthYear'].max())
    actor_death = actor_data['deathYear'].isnull().any()
    details, blank = st.columns([1.5, 4.5])
    with details:
        stc.html(f"""<h1>Actor</h1><h4>Name:{select}</h4><h4>Birth Year:{actor_birth}</h4>""")
    try:
        details.image(search_actor(select), width=150)
    except Exception:
        details.write("Network Faild")
    if not actor_death:
        st.write(f"Death Year:{int(actor_data['deathYear'].max())}")
    with blank:
        select = st.selectbox('Select', ['Rating', 'Popularity'])
        if select == 'Rating':
            actor_data = actor_data.sort_values(by='averageRating', ascending=False)
            fig1 = px.bar(actor_data, x='originalMovieTitle', y='averageRating', color='averageRating')
            fig1.update_layout(showlegend=False, width=900, height=450, autosize=True, legend_valign='top')
            st.write(fig1)
        if select == 'Popularity':
            actor_data = actor_data.sort_values(by='numVotes', ascending=False)
            fig1 = px.bar(actor_data, x='originalMovieTitle', y='numVotes', color='numVotes')
            fig1.update_layout(showlegend=False, width=900, height=450, autosize=True, legend_valign='top')
            st.write(fig1)
    actor_data = actor_data.drop(['actorName', 'deathYear', 'birthYear'], axis=1)
    actor_data['MovieId']=[i for i in range(1, len(actor_data.index)+1)]
    actor_data = actor_data.set_index('MovieId')
    actor_data_year = actor_data.groupby(actor_data['startYear']).mean()
    actor_data_genre = actor_data.groupby(actor_data['genre']).mean()
    actor_data_rtime = actor_data.groupby(actor_data['runtimeMinutes']).mean()
    graph1, graph11, graph2 = st.columns([1, 1, 2])
    grapha = graph1.selectbox('', ['Average Rating over', 'Number of votes over'])
    graph = graph11.selectbox('  ', ['Year','Genre','Run time'])
    graphy = graph2.selectbox('Number of votes over', ['Genre', 'Adult or not'])
    if grapha == 'Average Rating over':
        if graph == 'Year':
            graph1.write(actors_graphs(actor_data_year, 'averageRating'))
        if graph == 'Genre':
            graph1.write(actors_graphs(actor_data_genre, 'averageRating'))
        if graph == 'Run time':
            graph1.write(actors_graphs(actor_data_rtime, 'averageRating'))
    if grapha == 'Number of votes over':
        if graph == 'Year':
            graph1.write(actors_graphs(actor_data_year, 'numVotes'))
        if graph == 'Genre':
            graph1.write(actors_graphs(actor_data_genre, 'numVotes'))
        if graph == 'Run time':
            graph1.write(actors_graphs(actor_data_rtime, 'numVotes'))
    if graphy == 'Adult or not':
        graph2.write(actors_graphs_pie(actor_data, 'isAdult'))
    if graphy == 'Genre':
        graph2.write(actors_graphs_pie(actor_data, 'genre'))


def actors_graphs(data_frame, y_axis):
    fig = px.bar(data_frame, x=data_frame.index, y=y_axis, color=y_axis)
    fig.update_layout(showlegend=False, width=550, height=350, autosize=True)
    return fig


def actors_graphs_pie(data_frame, value):
    fig = px.pie(data_frame, names=value , color_discrete_sequence=px.colors.sequential.Plasma_r)
    fig.update_layout(showlegend=True, width=550, height=350, autosize=True)
    return fig


def search_actor(name):
    name = name.split(' ')
    sename=''
    for j in name:
        sename += str(j) + '+'
    sename = sename[:-1]
    url = 'https://www.google.co.uk/search?q='+sename+'&hl=en&source=lnms&tbm=isch&sa=X&ved=2ahUKEwjJ35WL9KbyAhXs7HMBHR' \
                                                      'A3CkcQ_AUoAXoECAEQAw&biw=1093&bih=530'
    r = rq.get(url)
    sp = bs(r.text, 'html.parser')
    im = sp.findAll('img')
    for i in im:
        pattern = r'https://'
        if re.match(pattern, i['src']):
            return i['src']


def overview_of_datasheet(dataframe):
    st.header("Overview")
    with st.expander("Before Data Clean"):
        des = dataframe_uncleaned.describe()
        st.write("DataSheet overview", des)
        col1, space, col2 =st.columns([0.75, 0.25, 2])
        col1.write("Not available data count in each column")
        col1.write(dataframe_uncleaned.isnull().sum())
        fig1 = px.box(dataframe_uncleaned, y='runtimeMinutes', title="Runtime column data spread")
        col2.write(fig1)
        st.write(f'Number of duplicate rows in data set: {dataframe_uncleaned.duplicated().sum()}')
    with st.expander("After Data Clean"):
        des_clean = dataframe.describe()
        st.write("DataSheet overview", des_clean)
        col1, space, col2 = st.columns([0.75, 0.25, 2])
        col1.write("Not available data count in each column")
        col1.write(dataframe.isnull().sum())
        fig1 = px.box(dataframe, y='runtimeMinutes', title="Runtime column data spread")
        col2.write(fig1)
        st.write(f'Number of duplicate rows in data set: {dataframe.duplicated().sum()}')


def rating_overview():
    st.write("Rating overview")
    select = st.select_slider("select Rating value", options=[i/10 for i in range(20, 100)])
    data = dataframe.groupby(dataframe['averageRating'])
    df = pd.DataFrame()
    for rate, value in data:
        if select == rate:
            value = value.drop(['birthYear', 'deathYear', 'averageRating'], axis=1)
            df = value
            break
    st.write(df)
    col1, col2 = st.columns([1, 1])
    with col1:
        select = st.selectbox('Acording to Rating', ['Adult or Not', 'Genre'])
        if select == 'Adult or Not':
            st.write(actors_graphs_pie(df, 'isAdult'))
        if select == 'Genre':
            fig = px.pie(df, names='genre', color_discrete_sequence=px.colors.sequential.Plasma_r, labels=None)
            fig.update_layout(showlegend=True, width=550, height=500, autosize=True)
            st.write(fig)
    with col2:
        select = st.selectbox('Acordinsgdgsdgfg to Rating', ['Adult or Not', 'Genre'])
        if select == 'Adult or Not':
            fig = px.bar(df, x='originalMovieTitle', y='runtimeMinutes', color='runtimeMinutes')
            st.write(fig)
        if select == 'Genre':
            fig = px.pie(df, names='genre', color_discrete_sequence=px.colors.sequential.Plasma_r, labels=None)
            fig.update_layout(showlegend=True, width=550, height=500, autosize=True)
            st.write(fig)


def movie_overview():
    data = dataframe.drop(['deathYear', 'birthYear'], axis=1)
    data = data.groupby(dataframe['mainMovieTitle'])
    movie = ['']
    col1, col2 =st.columns(2)
    for i, j in data:
        movie.append(i)
    select = st.sidebar.selectbox("Select a Movie", movie, index=0)
    for i, j in data:
        if i == select:
            if select.strip()[0] == '#':
                select = select[1:]
            if select.strip()[0] == '&':
                select = select[1:]
            with col1:
                stc.html(f"""<h1>Movie</h1><h4>Name:{select}</h4><h4>Year:{int(j['startYear'].iloc[0])}</h4>""")
                st.image(search_actor(select + " Movie"), width=150)
            with col2:
                name = ''
                for a in range(len(j['actorName'])):
                    name += j['actorName'].iloc[a] + '<br>'
                stc.html(f"""<h4>Actors<h4>{name}""")
            break


def main():
    select = st.sidebar.selectbox('Navigation', ["Overview of Datasheet", 'Overview of an Actor', 'Overview by Rating',
                                                 'Overview of a Movie'])
    if select == 'Overview of an Actor':
        sidebar()
    if select == 'Overview of Datasheet':
        overview_of_datasheet(dataframe)
    if select == 'Overview by Rating':
        rating_overview()
    if select == 'Overview of a Movie':
        movie_overview()


if __name__ == '__main__':
    main()
