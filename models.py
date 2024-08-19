from flask_sqlalchemy import SQLAlchemy
from flask_user import UserMixin
import pandas as pd
from sqlalchemy.orm import relationship

db = SQLAlchemy()

# Define the User data-model.
# NB: Make sure to add flask_user UserMixin as this adds additional fields and properties required by Flask-User
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean(), nullable=False, server_default='1')
    is_in_rating = db.Column( db.Boolean(), default=False, nullable=False)

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    username = db.Column(db.String(100, collation='NOCASE'), nullable=False)
    password = db.Column(db.String(255), nullable=False, server_default='')
    email_confirmed_at = db.Column(db.DateTime())

    # User information
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')


class Movie(db.Model):
    __tablename__ = 'movies'
    movieId = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
    genres = db.relationship('MovieGenre', backref='movie', lazy=True)
    tag = db.relationship('MovieTags', backref='movie', lazy=True)
    link = db.relationship('MovieLinks', backref='movie', lazy=True)

class MovieGenre(db.Model):
    __tablename__ = 'movie_genres'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movieId'), nullable=False)
    genre = db.Column(db.String(255), nullable=False, server_default='')


class MovieTags(db.Model):
    __tablename__ = 'movieTags'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movieId = db.Column(db.Integer, db.ForeignKey('movies.movieId'), nullable=False)
    tag = db.Column(db.String(255), nullable=False, server_default='')
    timestamp = db.Column(db.Integer, nullable=False)


class MovieLinks(db.Model):
    __tablename__ = 'movieLinks'
    id = db.Column(db.Integer, primary_key=True)
    movieId = db.Column(db.Integer, db.ForeignKey('movies.movieId'), nullable=False)
    imdbId = db.Column(db.String(100), nullable=False, server_default='')
    tmdbId = db.Column(db.String(100), nullable=False, server_default='')


class Rating (db.Model):
    __tablename__ = 'rating'
    movieId = db.Column(db.Integer, db.ForeignKey('movies.movieId'), nullable=False, primary_key=True)
    userIdRate = db.Column(db.Integer, primary_key = True, nullable=False)
    rating= db.Column(db.Integer, nullable= False, server_default = '1')
    timestamp = db.Column(db.Integer, nullable=False)


class UserPreferredGenres(db.Model):
    __tablename__ = 'userPreferences'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    genre = db.Column(db.String(255), server_default='')

#class UserInRatingFile (db.Model): 
   