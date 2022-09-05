import pickle
import re
import numpy as np
import pandas as pd
from nltk.tokenize import RegexpTokenizer
from surprise import KNNBasic
from surprise import Reader, Dataset

df = pd.read_csv('static/files/movies/metadata_clean.csv', dtype='unicode')

links_small = pd.read_csv('static/files/movies/links_small.csv')[['movieId', 'tmdbId']]
links2 = links_small
links_small = links_small[links_small['tmdbId'].notnull()]['tmdbId'].astype('int')

df['id'] = df['id'].astype('int')
sdf = df[df['id'].isin(links_small)]

'''
Cleaning functions 
'''


def remueve_valores_no_ascii(string):
    return "".join(c for c in string if ord(c) < 128)


def pasar_a_minusculas(texto):
    return texto.lower()


def remover_puntuacion(texto):
    tokenizer = RegexpTokenizer(r'\w+')
    texto = tokenizer.tokenize(texto)
    texto = " ".join(texto)
    return texto


def elimina_codigos_html(texto):
    html = re.compile('<.*?>')
    return html.sub(r'', texto)


sdf.loc[:, 'tagline'] = sdf.loc[:, 'tagline'].fillna('')
sdf.loc[:, 'description'] = sdf.loc[:, 'overview'] + sdf.loc[:, 'tagline']
sdf.loc[:, 'description'] = sdf.loc[:, 'description'].fillna('')
sdf.loc[:, 'description'] = sdf.loc[:, 'description'].apply(remueve_valores_no_ascii)
sdf.loc[:, 'description'] = sdf.loc[:, 'description'].apply(pasar_a_minusculas)
sdf.loc[:, 'description'] = sdf.loc[:, 'description'].apply(remover_puntuacion)
sdf.loc[:, 'description'] = sdf.loc[:, 'description'].apply(elimina_codigos_html)

filename = 'cosine_sim_movies.sav'
cosine_sim = pickle.load(open(filename, 'rb'))

sdf = sdf.reset_index()
titles = sdf['title']

filename = 'sim_map_movies.sav'
cosine_sim_map = pickle.load(open(filename, 'rb'))
cosine_sim_map.head()

reader = Reader()
ratings = pd.read_csv('static/files/movies/ratings_small.csv')
ratings.head()

data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)

trainset = data.build_full_trainset()

# Build an algorithm, and train it.
knn = KNNBasic()
knn.fit(trainset)


# create the function to convert to int
def convert_int(x):
    try:
        return int(x)
    except:
        return np.nan


# Build title to ID and ID to title mappings
id_map = links2
id_map['tmdbId'] = id_map['tmdbId'].apply(convert_int)
id_map.columns = ['movieId', 'id']
id_map = id_map.merge(sdf[['title', 'id']], on='id').set_index('title')

# Build title to ID and ID to title mappings
id_to_title = id_map.set_index('id')


def hybrid_movies_reco(userid, title, n_rec):
    try:
        # Extract the cosine_sim index of the movie
        idx = cosine_sim_map[title]
        n_rec = convert_int(n_rec)
        userid = convert_int(userid)

        # print(str(userid) + ' - ' + title + ' - ' + str(n_rec))
        # Extract the similarity scores and their corresponding index for every movie from the cosine_sim matrix
        sim_scores = list(enumerate(cosine_sim[int(idx)]))

        # Sort the (index, score) tuples in decreasing order of similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Select the top 25 tuples, excluding the first
        # (as it is the similarity score of the movie with itself)
        sim_scores = sim_scores[1:26]

        # Store the cosine_sim indices of the top 25 movies in a list
        movie_indices = [i[0] for i in sim_scores]

        # Extract the metadata of the aforementioned movies
        movies = sdf.iloc[movie_indices][['title', 'vote_count', 'vote_average', 'year', 'id']]

        # Compute the predicted ratings using the KNN filter
        movies['est'] = movies['id'].apply(lambda x: knn.predict(userid, id_to_title.loc[x]['movieId']).est)

        # Sort the movies in decreasing order of predicted rating
        movies = movies.sort_values('est', ascending=False)

        # Return the top n movies as recommendations
        return movies.head(n_rec)

    except Exception as e:
        print(e)

# print(hybrid_movies_reco(1, 'Toy Story', 10))
