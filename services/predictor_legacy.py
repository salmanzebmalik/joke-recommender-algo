from flask import Flask, request, jsonify
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
import pandas as pd

app = Flask(__name__)

# Train the recommendation model on initial dataset
def train_model(data, params):
    reader = Reader(rating_scale=(-10, 10))
    dataset = Dataset.load_from_df(data[['userId', 'jokeId', 'rating']], reader)
    trainset = dataset.build_full_trainset()
    algo = SVD(n_factors=params['n_factors'],
           n_epochs=params['n_epochs'],
           lr_all=params['lr_all'],
           reg_all=params['reg_all'])
    algo.fit(trainset)
    return algo

# Predict missing ratings and create the matrix
def create_prediction_matrix(data, model):
    users = data['userId'].unique()
    jokes = data['jokeId'].unique()

    prediction_matrix = []
    for user in users:
        for joke in jokes:
            existing_rating = data.loc[(data['userId'] == user) & (data['jokeId'] == joke), 'rating']
            if not existing_rating.empty:
                prediction_matrix.append({
                    "userId": user,
                    "jokeId": joke,
                    "rating": existing_rating.iloc[0],
                    "type_of_rating": "actual"
                })
            else:
                predicted_rating = model.predict(user, joke).est
                prediction_matrix.append({
                    "userId": user,
                    "jokeId": joke,
                    "rating": predicted_rating,
                    "type_of_rating": "predictive"
                })
    return prediction_matrix

def predict(json_data):
    try:
        ratings_df = pd.DataFrame(json_data["ratings"])
        # Validate input
        required_columns = {'userId', 'jokeId', 'rating'}
        if not required_columns.issubset(ratings_df.columns):
            return jsonify({"error": "Missing required columns in input JSON"}), 400

        # Train the recommendation model
        model = train_model(ratings_df, json_data["params"])

        # Create the prediction matrix
        prediction_matrix = create_prediction_matrix(ratings_df, model)

        # Return the prediction matrix as JSON
        return jsonify(prediction_matrix)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
