from flask import Flask, request
import tensorflow as tf
from joblib import load
import api_util as au
import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer

app = Flask(__name__)

#Load Vocabulary and Count Vectorizer params
# Load the vocabulary and parameters
with open('Server/Models/cv_vocab.pkl', 'rb') as f:
    vocab = pickle.load(f)

with open('Server/Models/cv_params.pkl', 'rb') as f:
    params = pickle.load(f)
# Recreate the CountVectorizer
# Remove 'vocabulary' from params
if 'vocabulary' in params:
    del params['vocabulary']
        
cv = CountVectorizer(vocabulary=vocab, **params)
# Load Naive Bayes model
naive_bayes_model = load("Server/Models/model_NB.joblib")

@app.route("/")
def root_server():
    return "Conection succesfully built"

@app.route('/NaiveBayesPredict', methods=['POST'])
def naive_bayes_predict():
    data = request.get_json()  # Parse the JSON data from the request
    message = au.process_message(data)# Get the email object
    df_message = pd.DataFrame({'message': [message.message]})
    message_array = cv.fit_transform(df_message['message'].apply(lambda x: ' '.join(x))).toarray()
    prediction = naive_bayes_model.predict(message_array)
    return str(prediction[0])


if __name__ == '__main__':
    #Run Flask app
    app.run(port=8080, debug=True)