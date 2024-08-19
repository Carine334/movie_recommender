import csv
from sqlalchemy.exc import IntegrityError
from models import Movie, MovieGenre, MovieTags, MovieLinks, db, Rating, User
import pandas as pd
import sqlite3

def check_and_read_data(db):
    # check if we have movies in the database
    # read data if database is empty
    #if Movie.query.count() == 0:
    # read movies from csv
    with open('data/movies.csv', newline='', encoding='utf8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        count = 0
        for row in reader:
            if count > 0:
                try:
                    movieId = row[0]
                    title = row[1]
                    movie = Movie(movieId=movieId, title=title)
                    db.session.add(movie)
                    genres = row[2].split('|')  # genres is a list of genres
                    for genre in genres:  # add each genre to the movie_genre table
                        movie_genre = MovieGenre(movie_id=movieId, genre=genre)
                        db.session.add(movie_genre)
                    db.session.commit()  # save data to database
                except IntegrityError:
                    print("Ignoring duplicate movie: " + title)
                    db.session.rollback()
                    pass
            count += 1
            if count % 100 == 0:
                print(count, " movies read")
    

    #if MovieTags.query.count() == 0:
    # read tags from csv
    with open('data/tags.csv', newline='', encoding='utf8') as file:
        reader_1 = csv.reader(file, delimiter=',')
        count_bis = 0
        for row in reader_1:
            if count_bis > 0:
                try:
                    userId = row[0]
                    movieId = row[1]
                    tag = row[2]
                    timestamp = row[3]
                    new_movie_tag = MovieTags(userId=userId, movieId=movieId, tag =tag, timestamp=timestamp)
                    
                    db.session.add(new_movie_tag)
                    db.session.commit()  # save data to database
                
                except IntegrityError:
                    print("Ignoring duplicate movie: " + movieId)
                    db.session.rollback()
                    pass
            count_bis += 1
            if count_bis % 100 == 0:
                print(count_bis, " tags read")



    #if MovieLinks.query.count() == 0:
    # read links from csv
    with open('data/links.csv', newline='', encoding='utf8') as file:
        reader_2 = csv.reader(file, delimiter=',')
        count_2 = 0
        for row in reader_2:
            if count_2 > 0:
                try:
                    movieId = row[0]
                    imdb_id = row[1]
                    tmdb_id = row[2]
                    new_movie_link = MovieLinks( movieId=movieId, imdbId =imdb_id, tmdbId = tmdb_id)
                    db.session.add(new_movie_link)
                    db.session.commit()  # save data to database
                except IntegrityError:
                    print("Ignoring links for duplicate movie: " + movieId)
                    db.session.rollback()
                    pass
            count_2 += 1
            if count_2 % 100 == 0:
                print(count_2, " links read")

    # read ratings from csv
    with open('data/test_ratings.csv', newline='', encoding='utf8') as file:
        reader_3 = csv.reader(file, delimiter=',')
        count_3 = 0
        for row in reader_3:
            if count_3 > 0:
                try:
                    userId = row[1]
                    movieId = row[0]
                    rating = row[2]
                    timestamp = row [3]
                    new_rating = Rating ( userIdRate=userId, movieId = movieId, rating = rating, timestamp = timestamp)
                    db.session.add(new_rating)
                    db.session.commit() 
            


                except IntegrityError:
                    print("Ignoring duplicate rating : " + userId, movieId)
                    db.session.rollback()
                         

                try:
                    userId = row[1]
                    new_user = User (id = userId, username = 'FromRating')
                    db.session.add(new_user)
                    db.session.commit()
                except IntegrityError:
                    print("Ignoring duplicate user: " + userId)
                    db.session.rollback()
                    pass

            count_3 += 1
            if count_3 % 100 == 0:
                print(count_3, " rating read")


#movie_complete = Rating.merge(Movies, on='movieId')
#movie_complete.head()