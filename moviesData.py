import streamlit as st
import pandas as pd
import plotly.express as px
import requests as rq
from bs4 import BeautifulSoup as bs
import re
import streamlit.components.v1 as stc
import plotly.graph_objects as go


dataframe = pd.read_csv("data source\\movies data 2.csv")
pd.set_option('max_columns', 11)


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
    actor_birth = int(actor_data['birthYear'].max())
    actor_death = actor_data['deathYear'].isnull().any()
    details, blank = st.columns([1.5, 4.5])
    with details:
        stc.html(f"""<h1>Actor</h1><h4>Name:{select}</h4><h4>Birth Year:{actor_birth}</h4>""")
    try:
        details.image(search_actor(select), width=175)
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
    graph1, graph2 = st.columns(2)
    graph = graph1.selectbox('Average rating over', ['Year','Genre','Run time'])
    graphy = graph2.selectbox('Number of votes over', ['Genre', 'Adult or not'])
    if graph == 'Year':
        graph1.write(actors_graphs(actor_data_year, 'averageRating'))
    if graph == 'Genre':
        graph1.write(actors_graphs(actor_data_genre, 'averageRating'))
    if graph == 'Run time':
        graph1.write(actors_graphs(actor_data_rtime, 'averageRating'))
    if graphy == 'Adult or not':
        actor_data['isAdult'] = actor_data['isAdult'].replace(0, 'Not Adult')
        actor_data['isAdult'] = actor_data['isAdult'].replace(1, 'Adult')
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
    des = dataframe.describe()
    st.write(des)
    st.write(dataframe.isnull().sum())
    dataframe = dataframe.sort_values(by='runtimeMinutes', ascending=False)
    st.write(dataframe)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=des.columns, y=des.loc['std'], name='min',
                         marker_color='rgb(55, 83, 109)'))
    #fig.add_trace(go.Bar(x=des.columns, y=des.loc['max'], name='max',
     #                    marker_color='rgb(26, 118, 255)'))
    fig.update_layout(title='Overview of Datasheet', bargap=0.15,  bargroupgap=0.1)
    st.write()
    col =des.columns
    st.plotly_chart(px.scatter(dataframe, y='runtimeMinutes', x='averageRating', color_discrete_sequence=px.colors.sequential.Plasma_r))
    st.plotly_chart(px.box(dataframe, y='runtimeMinutes', color_discrete_sequence=px.colors.sequential.Plasma_r))
    #st.write(dataframe)


def main():
    select = st.sidebar.selectbox('Navigation', ["Home", "Overview of Datasheet", 'Overview of an Actor'])
    if select == 'Overview of an Actor':
        sidebar()
    if select == 'Overview of Datasheet':
        overview_of_datasheet(dataframe)


if __name__ == '__main__':
    main()
