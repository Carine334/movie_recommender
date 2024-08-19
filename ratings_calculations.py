import pandas as pd
import numpy as np
from surprise import Reader, SVD, Dataset, accuracy
from surprise.model_selection import GridSearchCV, train_test_split, cross_validate
from models import *
from collections import defaultdict 
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix

#join the user table and the movie table using the relation with movieId
#have the necessary data
def merging_tables():
    movie_complete = db.session.query(Movie.movieId, Movie.title, Rating.userIdRate, Rating.rating, Rating.timestamp).join(Rating).all()
    movie_complete_df = pd.DataFrame(movie_complete, columns=['movieId','title', 'userId', 'Ratings', 'timestamp'])
    return(movie_complete_df)

def transformingTables():
    movies = db.session.query(Movie.movieId, Movie.title).all()
    df_movies = pd.DataFrame(movies, columns=['movieId','title'])
    ratings = db.session.query(Rating.movieId, Rating.userIdRate, Rating.rating).all()
    df_ratings = pd.DataFrame(ratings, columns=['movieId','userId', 'rating'])
    tags = db.session.query(MovieTags.movieId, MovieTags.userId, MovieTags.tag).all()
    df_tags= pd.DataFrame(tags, columns=['movieId','userId', 'tags'])
    return (df_movies, df_ratings, df_tags)

def matrix_def():
    #user-movie matrix based on ratings for our dataset
    #impute missing or null values with 0
    used_data= merging_tables()
    df_user_item_matrix = used_data.pivot(index=['movieId'], columns=['userId'], values='Ratings').fillna(0)
    #Sparse matrix representation
    user_item_matrix_sparse = csr_matrix(df_user_item_matrix.values)
    return (df_user_item_matrix, user_item_matrix_sparse)



def KNN_model():
    # Define a KNN model on cosine similarity
    model = NearestNeighbors(n_neighbors=30, metric='cosine', algorithm='brute', n_jobs=-1)
    user_item_matrix_sparse = matrix_def()[1]
    result = model.fit(user_item_matrix_sparse)
    return (result)



def useful():
    index_to_movie = dict()
    df_movies= transformingTables()[0]
    indexes=[]
    
    df_user_item_matrix = matrix_def()[0]

    df_titles_movies = df_movies.set_index('movieId').loc[df_user_item_matrix.index]
    count = 0

    for index, row in df_titles_movies.iterrows():

        index_to_movie[count]=row['title']

        count +=1
    return (index_to_movie)


def collaborative_based_recommender(model, user_item_matrix_sparse, df_movies, number_of_recommendations, movie_index):
    #Print 10 recommendations movies 
    #if the movies that is used as a base to the recommendations has receive some ratings
    #if the movie don't have any ratings, apply the content-based recommender function

    index_to_movie = useful()
    
    # Check if movie_index is a valid key in the dictionary
    if movie_index in index_to_movie:
        main_title = index_to_movie[movie_index]
        dist, ind = model.kneighbors(user_item_matrix_sparse[movie_index], n_neighbors=number_of_recommendations + 1 )
        
        dist = dist[0].tolist()

        ind = ind[0].tolist()
        titles = [] 

        for index in ind:
            print ('Checking: ', index_to_movie)
            print ("let's see : ", index_to_movie[index])
            titles.append(index_to_movie[index])

        recommendations = list(zip(titles,dist))  
        print (recommendations)  

        # sort recommendation
        recommendations_sorted = sorted(recommendations, key = lambda x:x[1])

        # reverse recommendations, leaving out the first element 
        recommendations_sorted.reverse()
        recommendations_sorted = recommendations_sorted[:-1]

        print("Recommendations for movie {}: ".format(main_title))
        text1 = [( "Because you well rated  {}: ".format(main_title) )]

        count = 0
        text2 = []
        for (title, distance) in recommendations_sorted:

            count += 1

            print('{}. {}, recommendation score = {}'.format(count, title, round(distance,3)))
            
            text2.append('{}. {}, recommendation score = {}'.format(count, title, round(distance,3)))

        return text1 + text2
    else:
        hint = ["No recommendation: Movie index not found in the dictionary"]
        # Handle the case when movie_index is not a valid key
        return hint
