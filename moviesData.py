import streamlit as st
import pandas as pd
import plotly.express as px
import requests as rq
from bs4 import BeautifulSoup as bs
import re
import streamlit.components.v1 as stc


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
    st.header("Actor")
    details, img,blank = st.columns([0.5,1.5,2])
    details.write(f'''
    Name :
    
    {select}\n
    Birth Year:
    
    {actor_birth}
    ''')
    img.image(search_actor(select), width=175)
    if not actor_death:
        st.write(f"Death Year:{int(actor_data['deathYear'].max())}")
    #actor_data = actor_data.drop(['actorName', 'deathYear', 'birthYear'], axis=1)
    actor_data['MovieId']=[i for i in range(1,len(actor_data.index)+1)]
    actor_data = actor_data.set_index('MovieId')
    fig1 = px.bar(actor_data, y='originalMovieTitle', x='averageRating', color='averageRating',orientation='h')
    fig1.update_layout(showlegend=False, width=600, height=350, autosize=True, legend_valign='top')
    blank.write(fig1)
    graph1, graph2 = st.columns(2)
    graph = graph1.selectbox('Average rating over', ['Time','Genre'])
    graphy = graph2.selectbox('Average wfhwjeb bjs', ['Time', 'Genre'])
    if graph == 'Time':
        fig = px.bar(actor_data, x='startYear', y='averageRating', color='averageRating')
        fig.update_layout(showlegend=False,width=600,height=400,autosize=True)
        graph1.write(fig)
    if graph == 'Genre':
        graph1.plotly_chart(px.scatter(actor_data, x='genre', y='averageRating', color='averageRating'))
    if graphy == 'Time':
        fig = px.bar(actor_data, x='startYear', y='averageRating', color='averageRating')
        fig.update_layout(showlegend=False,width=600,height=400,autosize=True)
        graph2.write(fig)
    if graphy == 'Genre':
        graph2.plotly_chart(px.scatter(actor_data, x='genre', y='averageRating', color='averageRating'))


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
    stc.html("<h1>Overview</h1>")
    st.write(dataframe.describe())


def main():
    select = st.sidebar.selectbox('Navigation', ["Overview of Datasheet", 'Overview of an Actor'],)
    if select == 'Overview of an Actor':
        sidebar()
    if select == 'Overview of Datasheet':
        overview_of_datasheet()


if __name__ == '__main__':
    main()


