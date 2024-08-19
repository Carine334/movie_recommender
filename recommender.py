# Contains parts from: https://flask-user.readthedocs.io/en/latest/quickstart_app.html

from flask import Flask, render_template, request
from flask_user import login_required, UserManager, current_user
from flask import g

from models import *
from read_data import check_and_read_data
from ratings_calculations import *
import time
import random
from sqlalchemy import any_

app= Flask(__name__, static_url_path='/static')


# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///movie_recommender.sqlite'  # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning

    # Flask-User settings
    USER_APP_NAME = "Movie Recommender"  # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False  # Disable email authentication
    USER_ENABLE_USERNAME = True  # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = True  # Simplify register form

    # make sure we redirect to home view, not /
    # (otherwise paths for registering, login and logout will not work on the server)
    USER_AFTER_LOGIN_ENDPOINT = 'home_page'
    USER_AFTER_LOGOUT_ENDPOINT = 'home_page'
    USER_AFTER_REGISTER_ENDPOINT = 'home_page'

# Create Flask app
app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')  # configuration
app.app_context().push()  # create an app context before initializing db
db.init_app(app)  # initialize database
db.create_all()  # create database if necessary
user_manager = UserManager(app, db, User)  # initialize Flask-User management


@app.cli.command('initdb')
def initdb_command():
    global db
    """Creates the database tables."""
    check_and_read_data(db)
    print('Initialized the database.')

# The Home page is accessible to anyone
@app.route('/')
def home_page():
    # render home.html template
    return render_template("home.html")




# The Members page is only accessible to authenticated users via the @login_required decorator
@app.route('/movies')
@login_required  # User must be authenticated
def movies_page():

    #links to access to the movies page in imdb or themoviedb
    domain_1 = "https://www.themoviedb.org/movie/"
    domain_2 = "https://www.imdb.com/title/tt"
    #retrieve the id of the connected user
    userId = current_user.id
    #Print all genres of movies available
    genres = []
    genres = db.session.query(MovieGenre.genre).distinct().all()
    
    #Print a list of movies to the user
    #If he defines somes preferences: show him the movies of the genres that he likes
    #If not, show him 10 movies
    genres_for_user = db.session.query(UserPreferredGenres.genre).filter(UserPreferredGenres.userId == userId).distinct().all()
    if not  genres_for_user:
        message = "Movies of our catalogue :"
        movies = Movie.query.limit(20).all()
    else: 
        # User has preferred genres, query the database for movies from those genres
        # Assuming genres_for_user is a list representing the user's preferred genres
        #for each genre, show him 3 movies 
        message = "Movies of your favorites genres :"
        list_id= []
        #manage the number of movies that is printed
        #When there is more than 3 preferred genres, print 4 movies for each genres
        #else print 7 movies for each one
        if len (genres_for_user) > 3:
            num_movies = 4
        else: num_movies = 7

        for single_genre in genres_for_user:
            selection = db.session.query(MovieGenre.movie_id).filter(MovieGenre.genre == single_genre[0]).distinct().limit(num_movies).all()
            for value in selection:
                list_id.append(value[0])
        #collect the title of the different movies using their id 
        movies =  []
        for identifier in list_id:
            movies_list = Movie.query.filter(Movie.movieId == identifier).all()
            movies.extend(movies_list)

        

    #recommend movies to the user based his positives votes
    #retrieve the id of each movie that the connected user has rated
    #Put the ids in a list   
    rated_movies = []
    rated = db.session.query (Rating.movieId, Rating.rating).filter(Rating.userIdRate == userId).all()
    #If the user has not rated movies yet
    if not rated: 
        no_recommendation= "You haven't rated movies yet !"
        recommended = " "
    #when he voted for some movies 
    else:
        #Choose a random movie that the user has rated over 3 to suggest others movies
        singleTuple = random.choice(rated)
        while singleTuple [1] < 3:
            singleTuple = random.choice(ratedm)

        #Parameters for our recommender system
        #Print 5 similars movies to a well-rated movie by the user
        model = KNN_model()
        user_item_matrix_sparse = matrix_def()[1]
        df_movies = transformingTables()[0]

        recommended = collaborative_based_recommender (model, user_item_matrix_sparse, df_movies, 5,  singleTuple [0] -1)
        no_recommendation = " "

    return render_template("movies.html", movies=movies, domain_1 = domain_1, domain_2 = domain_2, recommended = recommended, no_recommendation = no_recommendation, genres = genres, message = message)



@app.route('/rate', methods=['POST'])
@login_required  # User must be authenticated
def rate():
    movieid = request.form.get('movieid')
    movieid = movieid.replace(',', '')
    rating = request.form.get('rating')
    userid = current_user.id
    
    #if the user has already voted for a movie
    #update the rate with the new value
    #Otherwise, save the rating in the database 
    existing_rating = Rating.query.filter_by(movieId=movieid, userIdRate=userid).first()
    if existing_rating:
        existing_rating.rating = rating
        existing_rating.timestamp = time.time()
        db.session.commit()
        print("Updated rating for {} by {}".format(movieid, userid))
        update = "Updated rating {} Thank you ! ".format(rating)
        new_rate = " "
    else:
        new_rating = Rating(movieId=movieid, userIdRate=userid, rating=rating, timestamp=time.time())
        db.session.add(new_rating)
        db.session.commit()
        print("Rated {} for {} by {}".format(rating, movieid, userid))
        update = " "
        new_rate = "You have rated {}. Thank you !".format(rating)
    return render_template("rated.html", rating=rating, update = update, new_rate = new_rate)




@app.route('/preferences', methods=['POST'])
@login_required  # User must be authenticated
def preferences():
  

    #add  the preferences of the user in the database
    preferred_genres = []
    preferred_category = request.form.get('genres')
    preferred_genres.append(preferred_category)
    userid = current_user.id
    for g in preferred_genres:
        new_genre = UserPreferredGenres(userId= userid, genre = g)
        db.session.add(new_genre)
    db.session.commit()
    print("Preferrence successfully saved !")
    message = "Preferrence successfully saved !"

    return render_template("preferences.html", message = message, preferred_genres = preferred_genres)

# Start development web server
if __name__ == '__main__':
    app.run(port=5000, debug=True)
