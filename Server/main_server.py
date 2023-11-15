from flask import Flask, request
import tensorflow as tf
from joblib import load
import api_util as au
import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer

app = Flask(__name__)


with open('Server/Models/cv_vocab.pkl', 'rb') as f:
    vocab = pickle.load(f)

with open('Server/Models/cv_params.pkl', 'rb') as f:
    params = pickle.load(f)


if 'vocabulary' in params:
    del params['vocabulary']
    
#Modelo 2.0 con mas datos

with open('Server/Models/cv_vocab_1.pkl', 'rb') as f:
    vocab1 = pickle.load(f)

with open('Server/Models/cv_params_1.pkl', 'rb') as f:
    params1 = pickle.load(f)
# Recreate the CountVectorizer
# Remove 'vocabulary' from params
if 'vocabulary' in params1:
    del params1['vocabulary']
    

        
cv = CountVectorizer(vocabulary=vocab, **params)
cv1 = CountVectorizer(vocabulary=vocab1, **params1)

naive_bayes_model = load("Server/Models/model_NB.joblib")
naive_bayes_model_1 = load("Server/Models/model_NB_1.joblib")
@app.route("/", methods=['GET'])
def root_server():
    return "Server Alive"

@app.route('/NaiveBayesPredict', methods=['POST'])
def naive_bayes_predict():
    data = request.get_json()  
    message = au.clean_message(data['body'].split(" "))
    df_message = pd.DataFrame({'message': [message]})
    message_array = cv.fit_transform(df_message['message'].apply(lambda x: ' '.join(x))).toarray()
    prediction = naive_bayes_model.predict(message_array)
    return str(prediction[0])

@app.route('/NaiveBayesPredict1', methods=['POST'])
def naive_bayes_predict_1():
    data = request.get_json()  
    message = au.clean_message(data['body'].split(" "))
    df_message = pd.DataFrame({'message': [message]})
    message_array = cv1.fit_transform(df_message['message'].apply(lambda x: ' '.join(x))).toarray()
    prediction = naive_bayes_model_1.predict(message_array)
    return str(prediction[0])


if __name__ == '__main__':
    app.run(port=8081, debug=True)