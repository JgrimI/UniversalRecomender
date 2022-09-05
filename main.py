import re

import MySQLdb
from flask import Flask, request, session, redirect, url_for, render_template, jsonify
from flask_mysqldb import MySQL
import json

from books import book_recommender
from movies import hybrid_movies_reco
from songs import song_recommender

app = Flask(__name__)
    
# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = '12233445566'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'pythonlogin'

# Initialize MySQL
mysql = MySQL(app)


# http://localhost:5000/UniversalRecommender/ - this will be the login page
@app.route('/UniversalRecommender', methods=['GET', 'POST'])
def login():
    # connect
    conn = mysql.connection
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select count(*) as allcount from movies")
    rsallcount = cursor.fetchone()
    totalMovies = rsallcount['allcount']
    print(totalMovies)

    cursor.execute("select count(*) as allcount from songs")
    rsallcount = cursor.fetchone()
    totalSongs = rsallcount['allcount']
    print(totalSongs)

    cursor.execute("select count(*) as allcount from books")
    rsallcount = cursor.fetchone()
    totalBooks = rsallcount['allcount']
    print(totalBooks)

    # Output message if something goes wrong...
    msg = ''
    msgType = 0
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()

        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            # return 'Logged in successfully!'
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
            msgType = 1
            return render_template('distribution/customer-register.html', msg=msg, type=msgType)
    else:
        return render_template('distribution/index.html', msg=msg, movies=totalMovies, songs=totalSongs, books=totalBooks)


# http://localhost:5000/register - this will be the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    # connect
    conn = mysql.connection
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    # Output message if something goes wrong...
    msg = ''
    msgType = 0
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'name-login' in request.form and 'username-login' in request.form and \
            'password-login' in request.form and 'email-login' in request.form:
        # Create variables for easy access
        firstname = str(request.form['name-login'])
        lastname = str(request.form['last-login'])
        username = str(request.form['username-login'])
        password = str(request.form['password-login'])
        email = str(request.form['email-login'])

        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        usernameBD = cursor.fetchone()

        cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
        mail = cursor.fetchone()

        # If account exists show error and validation checks
        if usernameBD:
            msg = 'Username already exists!'
            msgType = 1
        elif mail:
            msg = 'Email already exists!'
            msgType = 1
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
            msgType = 1
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
            msgType = 1
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
            msgType = 1
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s, %s)', (username, password, email,
                                                                                      firstname, lastname))
            conn.commit()

            msg = 'You have successfully registered!'
            msgType = 2
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form2!'
        msgType = 1
    # Show registration form with message (if any)
    return render_template('distribution/customer-register.html', msg=msg, type=msgType)


# http://localhost:5000/home - this will be the home page, only accessible for loggedin users
@app.route('/')
def home():
    # Check if user is loggedin

    if 'loggedin' in session:
        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("select count(*) as allcount from movies")
        rsallcount = cursor.fetchone()
        totalMovies = rsallcount['allcount']
        print(totalMovies)

        cursor.execute("select count(*) as allcount from songs")
        rsallcount = cursor.fetchone()
        totalSongs = rsallcount['allcount']
        print(totalSongs)

        cursor.execute("select count(*) as allcount from books")
        rsallcount = cursor.fetchone()
        totalBooks = rsallcount['allcount']
        print(totalBooks)

        # User is loggedin show them the home page
        return render_template('distribution/index.html', username=session['username'], movies=totalMovies, songs=totalSongs, books=totalBooks )
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/account - this will be the home page, only accessible for loggedin users
@app.route('/my_account')
def my_account():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('distribution/customer-account.html', username=session['username'])
    # User is not loggedin redirect to login page

    msg = 'Please sing up or register!'
    msgType = 1
    return render_template('distribution/customer-register.html', msg=msg, type=msgType)


# http://localhost:5000/logout - this will be the logout page
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile():
    # Check if account exists using MySQL
    conn = mysql.connection

    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page

    msg = 'Please sing up or register!'
    msgType = 1
    return render_template('distribution/customer-register.html', msg=msg, type=msgType)


@app.route('/datatable')
def datatable():
    # df = pd.read_csv('static/files/metadata_clean.csv', dtype='unicode')

    # return render_template('datatable.html', tables=[df.to_html(classes='data')], titles=df.columns.values)
    if request.method == 'POST' and 'id_user' in request.form and 'number_reco' in request.form:
        print('entro post')
        # Create variables for easy access
        userid = request.form['id_user']
        number_reco = request.form['number_reco']
        movie_name = request.form['movie_name']
        print(str(userid) + ' -- ' + str(number_reco))
    elif request.method == 'GET':
        print('entro get')
        userid = request.args.get('id_user')
        number_reco = request.args.get('number_reco')
        movie_name = request.args.get('movie_name')
        print(str(userid) + ' -- ' + str(number_reco))

    return render_template('datatable.html', id_user=userid, movie_name=movie_name, number_reco=number_reco)


# @app.route("/moviesreco", methods=["POST", "GET"])
# def moviesreco():
#     # Option [1]
#     # row_json_data = csv_data.to_json(orient='records')
#
#     # Option [2]
#     # "response" = > 1,
#     # "json" = > $newResponse,
#     # "suggest" = > $suggest_keywords,
#     # "criteria" = > $criaux
#
#     hy = hybrid_movies_reco(1, 'Toy Story', 10)
#     final_row_data = []
#
#     for index, rows in hy.iterrows():
#         final_row_data.append(rows.to_dict())
#
#     json_result = {'response': 1, 'json': final_row_data}
#     # print(json_result)
#     draw=2
#     totalRecords=10
#     totalRecordwithFilter=10
#     response = {
#         'draw': draw,
#         'iTotalRecords': totalRecords,
#         'iTotalDisplayRecords': totalRecordwithFilter,
#         'aaData': final_row_data,
#     }
#     return response


@app.route('/movies_recommendation', methods=["POST", "GET"])
def movies_recommendation():
    # Check if user is loggedin
    if 'loggedin' in session:

        # return render_template('datatable.html', tables=[df.to_html(classes='data')], titles=df.columns.values)
        if request.method == 'POST' and 'id_user' in request.form and 'number_reco' in request.form:
            print('entro post')
            # Create variables for easy access
            userid = request.form['id_user']
            number_reco = request.form['number_reco']
            movie_name = request.form['movie_name']
            print(str(userid) + ' -- ' + str(number_reco) + ' -- ' + movie_name)
        elif request.method == 'GET':
            print('entro get')
            userid = request.args.get('id_user')
            number_reco = request.args.get('number_reco')
            movie_name = request.args.get('movie_name')
            print(str(userid) + ' -- ' + str(number_reco))

        return render_template('distribution/movies-recommendation.html', id_user=userid, movie_name=movie_name,
                               number_reco=number_reco)

    msg = 'Please sing up or register!'
    msgType = 1
    return render_template('distribution/customer-register.html', msg=msg, type=msgType)


@app.route('/songs_recommendation', methods=["POST", "GET"])
def songs_recommendation():
    # Check if user is loggedin
    if 'loggedin' in session:

        # return render_template('datatable.html', tables=[df.to_html(classes='data')], titles=df.columns.values)
        if request.method == 'POST' and 'id_user' in request.form and 'number_reco' in request.form:
            print('entro post')
            # Create variables for easy access
            userid = request.form['id_user']
            number_reco = request.form['number_reco']
            song_name = request.form['song_name']
            author_name = request.form['author_name']
            print(str(userid) + ' -- ' + str(number_reco) + ' -- ' + song_name + ' -- ' + author_name)
        elif request.method == 'GET':
            print('entro get')
            userid = request.args.get('id_user')
            number_reco = request.args.get('number_reco')
            song_name = request.form['song_name']
            author_name = request.form['author_name']
            print(str(userid) + ' -- ' + str(number_reco))

        return render_template('distribution/songs-recommendation.html', id_user=userid, song_name=song_name, author_name=author_name, number_reco=number_reco)

    msg = 'Please sing up or register!'
    msgType = 1
    return render_template('distribution/customer-register.html', msg=msg, type=msgType)


@app.route('/books_recommendation', methods=["POST", "GET"])
def books_recommendation():
    # Check if user is loggedin
    if 'loggedin' in session:

        # return render_template('datatable.html', tables=[df.to_html(classes='data')], titles=df.columns.values)
        if request.method == 'POST' and 'id_user' in request.form and 'number_reco' in request.form:
            print('entro post')
            # Create variables for easy access
            userid = request.form['id_user']
            number_reco = request.form['number_reco']
            book_name = request.form['book_name']
            print(str(userid) + ' -- ' + str(number_reco) + ' -- ' + book_name)
        elif request.method == 'GET':
            print('entro get')
            userid = request.args.get('id_user')
            number_reco = request.args.get('number_reco')
            book_name = request.form['book_name']
            print(str(userid) + ' -- ' + str(number_reco))

        return render_template('distribution/books-recommendation.html', id_user=userid, book_name=book_name, number_reco=number_reco)

    msg = 'Please sing up or register!'
    msgType = 1
    return render_template('distribution/customer-register.html', msg=msg, type=msgType)



@app.route("/moviesreco", methods=["POST", "GET"])
def moviesreco():
    # Check if user is loggedin
    if 'loggedin' in session:

        if request.method == 'POST' and 'id_user' in request.form and 'number_reco' in request.form:
            print('entro post movies')
            # Create variables for easy access
            userid = request.form['id_user']
            movie_name = request.form['movie_name']
            number_reco = request.form['number_reco']
            print(str(userid) + ' -- ' + str(number_reco) + ' -- ' + movie_name)
        elif request.method == 'GET':
            print('entro get movies')
            userid = request.args.get('id_user')
            movie_name = request.args.get('movie_name')
            number_reco = request.args.get('number_reco')
            print(str(userid) + ' -- ' + str(number_reco))

        # Option [1]
        # row_json_data = csv_data.to_json(orient='records')

        # Option [2]
        # "response" = > 1,
        # "json" = > $newResponse,
        # "suggest" = > $suggest_keywords,
        # "criteria" = > $criaux
        if userid != "" and movie_name != "" and number_reco != "":
            hy = hybrid_movies_reco(userid, str(movie_name), number_reco)

            # for index, rows in hy.iterrows():
            #     final_row_data.append(rows.to_dict())
            #
            #     print(final_row_data)
            final_row_data = hy.values.tolist()
            # print(final_row_data)
            print(len(final_row_data))
            print(final_row_data[1])
            if len(final_row_data) > 0:

                response = {
                    'response': 1,
                    'aaData': final_row_data,
                }
                return response
            else:
                response = {
                    'response': 2,
                }
                return response

        else:
            response = {
                'response': 2,
            }
            return response
    msg = 'Please sing up or register!'
    msgType = 1
    return render_template('distribution/customer-register.html', msg=msg, type=msgType)


@app.route("/songsreco", methods=["POST", "GET"])
def songsreco():
    # Check if user is loggedin
    if 'loggedin' in session:

        if request.method == 'POST' and 'id_user' in request.form and 'number_reco' in request.form\
                and 'song_name' in request.form and 'author_name' in request.form:
            print('entro post songs')
            # Create variables for easy access
            userid = request.form['id_user']
            song_name = request.form['song_name']
            author_name = request.form['author_name']
            number_reco = request.form['number_reco']
            print(str(userid) + ' -- ' + str(number_reco) + ' -- ' + song_name + ' -- ' + author_name)
        elif request.method == 'GET':
            print('entro get songs')
            userid = request.args.get('id_user')
            song_name = request.form['song_name']
            author_name = request.form['author_name']
            number_reco = request.args.get('number_reco')

            print(str(userid) + ' -- ' + str(number_reco))

        if song_name != "" and author_name != "" and number_reco != "":
            sg = song_recommender(str(song_name), str(author_name), int(number_reco))

            final_row_data = sg.values.tolist()
            # print(final_row_data)
            print(len(final_row_data))
            print(final_row_data[1])
            if len(final_row_data) > 0:

                response = {
                    'response': 1,
                    'aaData': final_row_data,
                }
                return response
            else:
                response = {
                    'response': 2,
                }
                return response

        else:
            response = {
                'response': 2,
            }
            return response
    msg = 'Please sing up or register!'
    msgType = 1
    return render_template('distribution/customer-register.html', msg=msg, type=msgType)

@app.route("/booksreco", methods=["POST", "GET"])
def booksreco():
    # Check if user is loggedin
    if 'loggedin' in session:

        if request.method == 'POST' and 'id_user' in request.form and 'number_reco' in request.form\
                and 'book_name' in request.form:
            print('entro post songs')
            # Create variables for easy access
            userid = request.form['id_user']
            book_name = request.form['book_name']
            number_reco = request.form['number_reco']
            print(str(userid) + ' -- ' + str(number_reco) + ' -- ' + book_name)
        elif request.method == 'GET':
            print('entro get songs')
            userid = request.args.get('id_user')
            book_name = request.form['book_name']
            number_reco = request.args.get('number_reco')

            print(str(userid) + ' -- ' + str(number_reco))

        if book_name != "" and number_reco != "":
            bk = book_recommender(str(book_name), int(number_reco))

            final_row_data = bk.values.tolist()
            # print(final_row_data)
            print(len(final_row_data))
            print(final_row_data[1])
            if len(final_row_data) > 0:

                response = {
                    'response': 1,
                    'aaData': final_row_data,
                }
                return response
            else:
                response = {
                    'response': 2,
                }
                return response

        else:
            response = {
                'response': 2,
            }
            return response
    msg = 'Please sing up or register!'
    msgType = 1
    return render_template('distribution/customer-register.html', msg=msg, type=msgType)



@app.route("/movies-category", methods=["POST", "GET"])
def movies_category():
    # Check if user is loggedin
    if 'loggedin' in session:
        return render_template('distribution/movies-category-full.html')
    msg = 'Please sing up or register!'
    msgType = 1
    return render_template('distribution/customer-register.html', msg=msg, type=msgType)


@app.route("/songs-category", methods=["POST", "GET"])
def songs_category():
    # Check if user is loggedin
    if 'loggedin' in session:
        return render_template('distribution/songs-category-full.html')
    msg = 'Please sing up or register!'
    msgType = 1
    return render_template('distribution/customer-register.html', msg=msg, type=msgType)


@app.route("/books-category", methods=["POST", "GET"])
def books_category():
    # Check if user is loggedin
    if 'loggedin' in session:
        return render_template('distribution/books-category-full.html')
    msg = 'Please sing up or register!'
    msgType = 1
    return render_template('distribution/customer-register.html', msg=msg, type=msgType)


@app.route("/ajax_movies", methods=["POST", "GET"])
def ajax_movies():
    try:
        conn = mysql.connection

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]
            print(draw)
            print(row)
            print(rowperpage)
            print(searchValue)

            # Total number of records without filtering
            cursor.execute("select count(*) as allcount from movies")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']
            print(totalRecords)

            # Total number of records with filtering
            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute("SELECT count(*) as allcount from movies WHERE title LIKE %s OR overview LIKE %s OR "
                           "original_title LIKE %s OR tagline LIKE %s",
                           (likeString, likeString, likeString, likeString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']
            print(totalRecordwithFilter)

            ## Fetch records
            if searchValue == '':
                cursor.execute("SELECT * FROM movies ORDER BY vote_count desc  limit %s, %s;", [row, rowperpage])
                employeelist = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT * FROM movies WHERE title LIKE %s OR overview LIKE %s OR "
                    "original_title LIKE %s OR tagline LIKE %s limit %s, %s;",
                    (likeString, likeString, likeString, likeString, row, rowperpage))
                employeelist = cursor.fetchall()

            idu = session['id']
            data = []
            for row in employeelist:

                collection = row['belongs_to_collection']

                # poster = row['poster_path']
                if collection != "":
                    col = str(collection.replace("'", '"'))
                    y = json.loads(col)
                    col = "https://www.themoviedb.org/t/p/w500" + y["poster_path"]
                else:
                    col = "https://blackmantkd.com/wp-content/uploads/2017/04/default-image-620x600.jpg"

                # img="https://image.tmdb.org/t/p/w500"+poster
                title = '<div class="row text-center">' \
                        '<div class="col-12"><img src="' + col + '" alt="" class="thumb-sm rounded-circle mr-2">' \
                                                                 '</div><div class="col-12"><p>' + row['title'] + '</p>' \
                                                                                                                  '</div>' \
                                                                                                                  '</div>'

                data.append({
                    'title': title,
                    'overview': row['overview'],
                    'release_date': row['release_date'],
                    'vote_average': row['vote_average'],
                    'vote_count': row['vote_count'],
                    'actions': '<div><a data-toggle="dropdown" href="#" role="button" aria-haspopup="false" '
                               'aria-expanded="false"><button type="button" class="btn btn-gradient-danger '
                               'waves-effect" '
                               'style="min-width:100%;max-width:100%">Show More</button></a><div class="dropdown-menu '
                               'dropdown-menu-right profile-dropdown border-3"><a class="dropdown-item" '
                               'href="javascript:void(0);" onclick="openModalRate(' + str(row['id']) + ', 4)">'
                               '<i class="fas fa-star-half-alt text-gradient-danger"></i> Rate</a>'
                               '<a class="dropdown-item" href="javascript:void(0);" '
                               'onclick="openModalReco(' + str(idu) + ',\'' +
                               row['title'] + '\')">'  # change 1 to user id in session
                                              '<i class="fas fa-video text-gradient-danger"></i> Get Recommendations</a></div>'
                })

            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)

    except Exception as e:
        print(e)


@app.route("/ajax_songs", methods=["POST", "GET"])
def ajax_songs():
    try:
        conn = mysql.connection

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]
            print(draw)
            print(row)
            print(rowperpage)
            print(searchValue)

            # Total number of records without filtering
            cursor.execute("select count(*) as allcount from songs")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']
            print(totalRecords)

            # Total number of records with filtering
            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute("SELECT count(*) as allcount from songs WHERE song LIKE %s OR artist LIKE %s OR "
                           "text LIKE %s",[likeString, likeString, likeString])
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']
            print(totalRecordwithFilter)

            ## Fetch records
            if searchValue == '':
                cursor.execute("SELECT * FROM songs ORDER BY artist asc  limit %s, %s;", [row, rowperpage])
                employeelist = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT * FROM songs WHERE song LIKE %s OR artist LIKE %s OR text LIKE %s limit %s, %s;",
                    [likeString, likeString, likeString, row, rowperpage])
                employeelist = cursor.fetchall()

            idu = session['id']
            data = []
            for row in employeelist:

                data.append({
                    'song': row['song'],
                    'artist': row['artist'],
                    'lyrics': row['text'],
                    'actions': '<div><a data-toggle="dropdown" href="#" role="button" aria-haspopup="false" '
                       'aria-expanded="false"><button type="button" class="btn btn-gradient-danger '
                       'waves-effect" '
                       'style="min-width:100%;max-width:100%">Show More</button></a><div class="dropdown-menu '
                       'dropdown-menu-right profile-dropdown border-3"><a class="dropdown-item" '
                       'href="javascript:void(0);" onclick="openModalRate(' + str(row['id']) + ', 4)">'
                       '<i class="fas fa-star-half-alt text-gradient-danger"></i> Rate</a>'
                       '<a class="dropdown-item" href="javascript:void(0);" '
                       'onclick="openModalReco(' + str(idu) + ',\'' + row['song'] + '\',\'' + row['artist'] + '\')">'
                       '<i class="fas fa-video text-gradient-danger"></i> Get Recommendations</a></div>'
                })

            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)

    except Exception as e:
        print(e)



@app.route("/ajax_books", methods=["POST", "GET"])
def ajax_books():
    try:
        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]
            print(draw)
            print(row)
            print(rowperpage)
            print(searchValue)

            # Total number of records without filtering
            cursor.execute("select count(*) as allcount from books")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']
            print(totalRecords)

            # Total number of records with filtering
            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute("SELECT count(*) as allcount from books WHERE Book_Title LIKE %s OR authors LIKE %s OR "
                           "Book_genres LIKE %s",[likeString, likeString, likeString])
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']
            print(totalRecordwithFilter)

            ## Fetch records
            if searchValue == '':
                cursor.execute("SELECT * FROM books ORDER BY Wikipedia_article_ID asc  limit %s, %s;", [row, rowperpage])
                employeelist = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT * FROM books WHERE Book_Title LIKE %s OR authors LIKE %s OR "
                    "Book_genres LIKE %s limit %s, %s;",
                    [likeString, likeString, likeString, row, rowperpage])
                employeelist = cursor.fetchall()

            idu = session['id']
            data = []
            for row in employeelist:
                if row['Book_genres'] == "":
                    row['Book_genres'] = "Not Available"
                if row['Publication_date'] == "":
                    row['Publication_date'] = "Not Available"
                if row['authors'] == "":
                    row['authors'] = "Not Available"

                data.append({
                    'title': row['Book_Title'],
                    'authors': row['authors'],
                    'date': row['Publication_date'],
                    'genres': row['Book_genres'],
                    'plot': row['Plot_summary'],
                    'actions': '<div><a data-toggle="dropdown" href="#" role="button" aria-haspopup="false" '
                       'aria-expanded="false"><button type="button" class="btn btn-gradient-danger '
                       'waves-effect" '
                       'style="min-width:100%;max-width:100%">Show More</button></a><div class="dropdown-menu '
                       'dropdown-menu-right profile-dropdown border-3"><a class="dropdown-item" '
                       'href="javascript:void(0);" onclick="openModalRate(' + str(row['Wikipedia_article_ID']) + ')">'
                       '<i class="fas fa-star-half-alt text-gradient-danger"></i> Rate</a>'
                       '<a class="dropdown-item" href="javascript:void(0);" '
                       'onclick="openModalReco(' + str(idu) + ',\'' + row['Book_Title'] + '\')">'
                       '<i class="fas fa-video text-gradient-danger"></i> Get Recommendations</a></div>'
                })

            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    app.run(debug=True)
