# The import of the libraries is carried out
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import re
from nltk.tokenize import RegexpTokenizer

# The dataset is loaded from the json file

dtf1 = pd.read_json('static/files/songdata.json', orient='columns')

dtf1 = pd.json_normalize(dtf1['results'], max_level=1)
dtf1 = dtf1.drop(['link'],axis=1)
# The first 5 data of the dataset is printed
dtf1.head(5)


def remueve_valores_no_ascii(string):
    return "".join(c for c in string if ord(c) < 128)


def pasar_a_minusculas(texto):
    return texto.lower()


def remover_puntuacion(texto):
    tokenizer = RegexpTokenizer(r'\w+')
    texto = tokenizer.tokenize(texto)
    texto = " ".join(texto)
    return texto


def lyrics_url(texto):
    texto = "https://www.lyricsfreak.com/".join(texto)
    return texto


def elimina_codigos_html(texto):
    html = re.compile('<.*?>')
    return html.sub(r'', texto)


tfidf = TfidfVectorizer(min_df=1, stop_words='english')

# Data cleaning functions


# dtf1['link'] = dtf1['link'].apply(lyrics_url)
dtf1['text'] = dtf1['text'].fillna('')
dtf1['text'] = dtf1['text'].apply(remueve_valores_no_ascii)
dtf1['text'] = dtf1['text'].apply(elimina_codigos_html)

# Se convierte el dataset limpio a formato csv, agregandole indices
# dtf1.to_csv('songs_clean.csv', index=True)


# The TF-IDF matrix is built with the fit_transform method
tfidf_matrix = tfidf.fit_transform(dtf1['text'])
# matrix output
tfidf_matrix.shape

# this line calculates the cosine similarity matrix
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# This line builds a reverse mapping of book titles and indexes, and removes duplicate songs


def song_recommender(song, artist, n_songs, cosine_sim=cosine_sim, dtf1=dtf1):
    print(song + '- ' + artist)
    temp = dtf1[dtf1['song'] == song]
    temp = temp[temp['artist'] == artist]

    indices = pd.Series(temp.index, index=temp['song']).drop_duplicates()

    idx = indices[song]

    sim_scores = list(enumerate(cosine_sim[idx]))

    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:n_songs + 1]
    song_indices = [i[0] for i in sim_scores]

    return dtf1.iloc[song_indices]


"""
Books to consult:
1.Murder in LaMut
2.Jimmy the Hand
3.Miss Marple
4.Glittering Images
5.The Mad Ship
"""

# print(song_recommender('2001', 'Snoop Dogg', 10))
