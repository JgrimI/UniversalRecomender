# The import of the libraries is carried out
import json

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import re
from nltk.tokenize import RegexpTokenizer

# The dataset is loaded from the json file

dtf1 = pd.read_json('static/files/book.json', orient='columns')
dtf1 = pd.json_normalize(dtf1['results'], max_level=1)

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


def elimina_codigos_html(texto):
    html = re.compile('<.*?>')
    return html.sub(r'', texto)


def genres_to_list(text):
    if text != "":
        y = json.loads(text)
        y.keys()
        gen = []
        for key in y:
            gen.append(y[key])
            # print(y[key])

        return str(gen)
    else:
        return ""


tfidf = TfidfVectorizer(stop_words='english')


dtf1['Plot-summary'] = dtf1['Plot-summary'].fillna('')
dtf1['Plot-summary'] = dtf1['Plot-summary'].apply(remueve_valores_no_ascii)
dtf1['Plot-summary'] = dtf1['Plot-summary'].apply(pasar_a_minusculas)
dtf1['Plot-summary'] = dtf1['Plot-summary'].apply(remover_puntuacion)
dtf1['Plot-summary'] = dtf1['Plot-summary'].apply(elimina_codigos_html)

dtf1["Book-genres"] = dtf1["Book-genres"].apply(genres_to_list)

# dtf1.to_csv('books_clean.csv', index=False)

# The TF-IDF matrix is built with the fit_transform method
tfidf_matrix = tfidf.fit_transform(dtf1['Plot-summary'])
# matrix output
tfidf_matrix.shape

# this line calculates the cosine similarity matrix
similitud_coseno = linear_kernel(tfidf_matrix, tfidf_matrix)

# This line builds a reverse mapping of book titles and indexes, and removes duplicate titles
indices = pd.Series(dtf1.index, index=dtf1['Book-Title']).drop_duplicates()


def book_recommender(titulo, n_books, similitud_coseno=similitud_coseno, dtf1=dtf1, indices=indices):
    idx = indices[titulo]
    puntos_similitud = list(enumerate(similitud_coseno[idx]))

    puntos_similitud = sorted(puntos_similitud, key=lambda x: x[1], reverse=True)

    puntos_similitud = puntos_similitud[1:n_books + 1]

    libros_indices = [i[0] for i in puntos_similitud]

    dtf2 = dtf1.iloc[libros_indices]
    dtf2 = dtf2.drop(['Wikipedia-article-ID'], axis=1)
    dtf2 = dtf2.drop(['Freebase-ID'], axis=1)

    return dtf2

"""
Books to consult:
1.Murder in LaMut
2.Jimmy the Hand
3.Miss Marple
4.Glittering Images
5.The Mad Ship
"""

# print(book_recommender('The Sweetest Dream',10))
