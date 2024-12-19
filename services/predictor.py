from flask import Flask, request, jsonify
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Train the recommendation model on the dataset
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

# Batch predictions using the trained model
def batch_predict(users, jokes, ratings_dict, model):
    # Create a testset for all user-joke pairs
    testset = [(user, joke, 0) for user in users for joke in jokes]
    predictions = model.test(testset)

    # Create a dictionary for fast lookups
    predictions_dict = {(pred.uid, pred.iid): pred.est for pred in predictions}

    # Generate the prediction matrix
    prediction_matrix = []
    for user in users:
        for joke in jokes:
            key = (user, joke)
            if key in ratings_dict:
                prediction_matrix.append({
                    "userId": user,
                    "jokeId": joke,
                    "rating": ratings_dict[key],
                    "type_of_rating": "actual"
                })
            else:
                predicted_rating = predictions_dict.get(key, 0)  # Default value if prediction fails
                prediction_matrix.append({
                    "userId": user,
                    "jokeId": joke,
                    "rating": predicted_rating,
                    "type_of_rating": "predictive"
                })
    return prediction_matrix

# Main prediction function
def predict(json_data):
    try:
        ratings_df = pd.DataFrame(json_data["ratings"])

        # Validate input
        required_columns = {'userId', 'jokeId', 'rating'}
        if not required_columns.issubset(ratings_df.columns):
            return jsonify({"error": "Missing required columns in input JSON"}), 400

        # Convert ratings into a dictionary for fast lookups
        ratings_dict = ratings_df.set_index(['userId', 'jokeId'])['rating'].to_dict()

        # Get unique users and jokes
        users = ratings_df['userId'].unique()
        jokes = ratings_df['jokeId'].unique()

        # Train the recommendation model
        model = train_model(ratings_df, json_data["params"])

        # Batch predictions
        prediction_matrix = batch_predict(users, jokes, ratings_dict, model)

        # Return the prediction matrix as JSON
        return jsonify(prediction_matrix)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
