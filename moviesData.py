import streamlit as st
import pandas as pd
import plotly.express as px
import requests as rq
from bs4 import BeautifulSoup as bs
import re
import streamlit.components.v1 as stc

# Data Reading and Cleaning Part
dataframe = pd.read_csv("data source\\movies data 2.csv")
pd.set_option('max_columns', 11)
dataframe['startYear'] = dataframe['startYear'].astype('int64')
dataframe_uncleaned = dataframe
dataframe['isAdult'] = dataframe['isAdult'].replace(0, 'Not Adult')
dataframe['isAdult'] = dataframe['isAdult'].replace(1, 'Adult')
dataframe = dataframe.drop_duplicates()  # remove duplicates
dataframe = dataframe.dropna(subset=['genre'])  # remove not available values in genre
dataframe = dataframe[dataframe['runtimeMinutes'] <= 240]  # remove all values of runtime above 240  minutes
dataframe = dataframe[dataframe['runtimeMinutes'] >= 10]  # remove all values of runtime bellow 10  minutes
dataframe = dataframe[dataframe['averageRating'] >= 2]  # remove all values of averagerating bellow 2  (855 rows)
dataframe_rating = dataframe.sort_values(by='averageRating', ascending=False)
dataframe_genre = dataframe.sort_values(by='genre', ascending=False)
dataframe_year = dataframe.groupby(dataframe['startYear'])


def adult_genre():
    dataframe_adult = dataframe.groupby(dataframe['isAdult'])
    a = []
    for i, j in dataframe_adult:
        a.append(j)
        return a[0], a[1]


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
            fig1 = px.bar(actor_data, x='mainMovieTitle', y='averageRating', color='averageRating')
            fig1.update_layout(showlegend=False, width=900, height=450, autosize=True, legend_valign='top')
            st.write(fig1)
        if select == 'Popularity':
            actor_data = actor_data.sort_values(by='numVotes', ascending=False)
            fig1 = px.bar(actor_data, x='mainMovieTitle', y='numVotes', color='numVotes')
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
    graphy = graph2.selectbox('  ', ['Genre', 'Adult or not'])
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
        fig1 = px.box(dataframe_uncleaned, y='runtimeMinutes', title="Runtime column data spread",
                      color_discrete_sequence=px.colors.sequential.Agsunset)
        col2.write(fig1)
        st.write(f'Number of duplicate rows in data set: {dataframe_uncleaned.duplicated().sum()}')
    with st.expander("After Data Clean"):
        des_clean = dataframe.describe()
        st.write("DataSheet overview", des_clean)
        col1, space, col2 = st.columns([0.75, 0.25, 2])
        col1.write("Not available data count in each column")
        col1.write(dataframe.isnull().sum())
        fig1 = px.box(dataframe, y='runtimeMinutes', title="Runtime column data spread",
                      color_discrete_sequence=px.colors.sequential.Agsunset)
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
    df['MovieId'] = [i for i in range(1, len(df.index) + 1)]
    df = df.set_index('MovieId')
    with st.expander("Dataframe"):
        df_drop = df.drop(['originalMovieTitle', 'isAdult', 'runtimeMinutes', 'genre', 'numVotes'], axis=1)
        st.write(df_drop)
    col1, col2, col3 = st.columns([1, 0.75, 0.25])
    with col1:
        select = st.selectbox('Acording to Rating', ['Adult or Not', 'Genre', ])
        if select == 'Adult or Not':
            fig = px.pie(df, names='isAdult', color_discrete_sequence=px.colors.sequential.Plasma_r)
            fig.update_layout(showlegend=True, width=550, height=500, autosize=True)
            st.write(fig)
        if select == 'Genre':
            fig = px.pie(df, names='genre', color_discrete_sequence=px.colors.sequential.Plasma_r, labels=None)
            fig.update_layout(showlegend=True, width=550, height=500, autosize=True)
            st.write(fig)
    with col2:
        select = st.selectbox(' Acordinsg to Rating ', ['Run time'])
        if select == 'Run time':
            fig = px.histogram(df, x='runtimeMinutes', color_discrete_sequence=px.colors.sequential.Agsunset)
            fig.update_layout(showlegend=True, width=475, height=450, autosize=True)
            st.write(fig)
    with col3:
        stc.html("     ")
        stc.html(f"""
        <html>
        <body bgcolor = '#F0F2F6' width='500' height='1500' >
        <h1 style='color:#4B2991;' ><center>{round(df['runtimeMinutes'].mean(),2)}</h1>
        <h3 style='color:#4B2991;' ><center>Average Runtime(min)</h3>
        </body>
        </html>
        """)


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


def top(sub, count=25):
    df = dataframe_rating.head(count)
    df = df.drop_duplicates(subset=sub)
    df['MovieId'] = [i for i in range(0, len(df))]
    df = df.set_index('MovieId')
    return df


def home():
    c1, c2 = st.columns([1, 4])
    c1.image("data source\\imbd.png")
    c2.title("Global View of Movies(2000-2020)")
    col1, col2, col3= st.columns([0.875, 2.125, 2])
    with col1:
        df = top('mainMovieTitle')
        st.title("Top Rated Movies")
        for a in range(11):
            st.write(df['mainMovieTitle'].iloc[a])
    with col2:
        year = []
        count = []
        meanrate = []
        mean_vote = []
        for y, d in dataframe_year:
            year.append(y)
            count.append(len(d))
            meanrate.append(d['averageRating'].mean())
            mean_vote.append(d['numVotes'].mean())
        fig = px.line(x=year, y=count, title='Number of movies on a particular year'
                      , color_discrete_sequence=px.colors.sequential.Agsunset)
        fig.update_layout(showlegend=False, width=500, height=350, autosize=True)
        st.write(fig)
    with col3:
        fig = px.pie(dataframe, names='isAdult', color_discrete_sequence=px.colors.sequential.Plasma_r,
                     title='Total Percentage of Adult and NonAdult movies', hole=0.3)
        fig.update_layout(showlegend=True, width=500, height=350, autosize=True)
        st.write(fig)
        fig = px.line(x=year, y=meanrate, title='Average Rating of a movie on a particular year',
                      color_discrete_sequence=px.colors.sequential.Agsunset)
        fig.update_layout(showlegend=False, width=500, height=350, autosize=True)
        st.write(fig)
    col4, col5, col6 = st.columns([0.875, 2.125, 2])
    with col4:
        df = top('genre', 100)
        st.title("Top Genres")
        name = ''
        for a in range(5):
            name += '\n'
            st.write(df['genre'].iloc[a])
    with col2:
        year = []
        adult = []
        notadult = []
        for i, j in dataframe_year:
            year.append(i)
            j = j.groupby(j['isAdult']).mean()
            try:
                notadult.append(j['averageRating'].iloc[0])
                adult.append(j['averageRating'].iloc[1])
            except:
                adult.append(0)
        addf = pd.DataFrame({'Year': year, 'Adult': adult, 'NonAdult': notadult})
        fig = px.line(addf, x='Year', y=['NonAdult', 'Adult'], title='Adult NonAdult average Rating',
                      color_discrete_sequence=px.colors.sequential.Plasma_r)
        fig.update_layout(showlegend=False, width=500, height=350, autosize=True)
        st.write(fig)
        #stc.html("<p style='color:#4B2991;'>Adult<font style='color:#00ff00;'>NonAdult</font></p>")
    with col5:
        fig = px.pie(dataframe['genre'], names=['Documentary', 'Drama', 'Comedy', 'Biography', 'Family'],
                     color_discrete_sequence=px.colors.sequential.Plasma_r,title='Top genres Percentage', hole=0.3)
        fig.update_layout(showlegend=True, width=500, height=350, autosize=True)
        st.write(fig)
    with col6:
        fig = px.line(x=year, y=mean_vote, title='Average Votes of a movie on a particular year',
                      color_discrete_sequence=px.colors.sequential.Agsunset)
        fig.update_layout(showlegend=False, width=500, height=350, autosize=True)
        st.write(fig)


def main():
    select = st.sidebar.selectbox('Navigation', ["Home", 'Overview of an Actor', 'Overview by Rating',
                                                 'Overview of a Movie', 'Overview of Datasheet'])
    if select == 'Overview of an Actor':
        sidebar()
    if select == 'Home':
        home()
    if select == 'Overview by Rating':
        rating_overview()
    if select == 'Overview of a Movie':
        movie_overview()
    if select == 'Overview of Datasheet':
        overview_of_datasheet(dataframe)


if __name__ == '__main__':
    main()
