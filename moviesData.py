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
        st.error("No internet connection")


def show_actor_data(select, data):
    actor_data = pd.DataFrame([])
    for i, j in data:
        if i == select:
            actor_data = j
    actor_birth = int(actor_data['birthYear'].max())
    actor_death = actor_data['deathYear'].isnull().any()
    details, img, blank = st.columns([0.5,0.5,1])
    with details:
        stc.html(f"""<h1>Actor</h1><h3>Name:{select}</h3><h3>Birth Year:{actor_birth}</h3>""")
    img.image(search_actor(select), width=175)
    if not actor_death:
        st.write(f"Death Year:{int(actor_data['deathYear'].max())}")
    actor_data = actor_data.drop(['actorName', 'deathYear', 'birthYear'], axis=1)
    actor_data['MovieId']=[i for i in range(1,len(actor_data.index)+1)]
    actor_data = actor_data.set_index('MovieId')
    fig1 = px.bar(actor_data, y='originalMovieTitle', x='averageRating', color='averageRating',orientation='h')
    fig1.update_layout(showlegend=False, width=600, height=350, autosize=True, legend_valign='top')
    blank.write(fig1)
    actor_data_year = actor_data.groupby(actor_data['startYear']).mean()
    actor_data_genre = actor_data.groupby(actor_data['genre']).mean()
    actor_data_rtime = actor_data.groupby(actor_data['runtimeMinutes']).mean()
    graph1, graph2 = st.columns(2)
    graph = graph1.selectbox('Average rating over', ['Time','Genre','Run time'])
    graphy = graph2.selectbox('Number of votes over', ['Time','Genre','Run time'])
    if graph == 'Time':
        graph1.write(actors_graphs(actor_data_year, 'averageRating'))
    if graph == 'Genre':
        graph1.write(actors_graphs(actor_data_genre, 'averageRating'))
    if graph == 'Run time':
        graph1.write(actors_graphs(actor_data_rtime, 'averageRating'))
    if graphy == 'Time':
        graph2.write(actors_graphs(actor_data_year, 'numVotes'))
    if graphy == 'Genre':
        graph2.write(actors_graphs(actor_data_genre, 'numVotes'))
    if graphy == 'Run time':
        graph2.write(actors_graphs(actor_data_rtime, 'numVotes'))


def actors_graphs(data_frame, y_axis):
    fig = px.bar(data_frame, x=data_frame.index, y=y_axis, color=y_axis)
    fig.update_layout(showlegend=False, width=600, height=400, autosize=True)
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
    print(im)
    for i in im:
        pattern = r'https://'
        if re.match(pattern, i['src']):
            return i['src']


def overview_of_datasheet():
    st.header("Overview")
    des = dataframe.describe()
    st.write(des)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=des.columns, y=des.loc['std'], name='min',
                         marker_color='rgb(55, 83, 109)'))
    #fig.add_trace(go.Bar(x=des.columns, y=des.loc['max'], name='max',
     #                    marker_color='rgb(26, 118, 255)'))
    fig.update_layout(title='Overview of Datasheet', bargap=0.15,  bargroupgap=0.1)
    st.write()
    col =des.columns
    st.plotly_chart(px.pie(des ))


def main():
    select = st.sidebar.selectbox('Navigation', ["Home", "Overview of Datasheet", 'Overview of an Actor'])
    if select == 'Overview of an Actor':
        sidebar()
    if select == 'Overview of Datasheet':
        overview_of_datasheet()


if __name__ == '__main__':
    main()
