#Import Libraries
import sqlite3
import re
from typing import Text
import pandas as pd

#imoort Flask Library
from flask import Flask, jsonify, request, make_response, render_template, redirect, url_for
from flasgger import Swagger, LazyJSONEncoder, LazyString
from flask_swagger_ui import get_swaggerui_blueprint

#Swagger UI
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.json_encoder = LazyJSONEncoder
swagger_template = dict(
info = {
    'title': LazyString(lambda: 'API Documentation for Pre-processed Data'),
    'version': LazyString(lambda: '1.0.0'),
    'description': LazyString(lambda: 'Documentation for API used in twitter text data processing procedure'),
        },
    host = LazyString(lambda: request.host)
)

#conneting database
data_base = sqlite3.connect('project-binar/data/goldchallenge.db', check_same_thread=False)
data_base.row_factory = sqlite3.Row
mycursor = data_base.cursor()
#defining & executing query command
#data from table is preprocessed text and cleaned text; variable type varchar
data_base.execute('''CREATE TABLE IF NOT EXISTS Twitter_Tweets (id INTEGER PRIMARY KEY AUTOINCREMENT, Texts varchar(255), Clean_Texts varchar(255));''')

# defining endpoint from user forms
SWAGGER_URL ='/docs'
API_URL = '/static/docs.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name':"Tweets Cleaner!"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

# welcomepage
@app.route('/', methods=['GET'])
def get():
  return "It's Time for C-C-C-Challenge!"

#text form endpoint
@app.route("/text", methods=["POST"])

def data():
    request.method == "POST"
    text = str(request.form["text"])
    #Clean text
    texts = re.sub("USER", " ", text)
    texts = re.sub('RT[\s]+', '', texts)
    texts = re.sub("URL", " ", texts)
    texts = re.sub('[^a-zA-Z0-9]', " ", texts)
    text_clean = re.sub("(http[s]?\://\S+)|([\[\(].*[\)\]])|([#@]\S+)|\n", " ", texts)
    #Insert new data to database
    query_text = "INSERT INTO Twitter_Tweets(Texts, Clean_Texts) values(?,?)"
    val = (text, text_clean)
    mycursor.execute(query_text, val)
    data_base.commit()
    print(text)
    print(text_clean)
    #API Response(s)
    json_response={
        'status_code': 200,
        'description': ("Texts are clean", "Data Successfully added"),
        'data': text_clean,
    }
    response_data = jsonify(json_response)
    return  response_data
  
    
   
#CSV endpoint
@app.route("/text/csv", methods=["POST"])
def input_csv():
  request.method == 'POST'
  file = request.files['file']
  data = pd.read_csv(file, encoding='iso-8859-1') #iso-8859-1 because UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf0
  text = data['T].tolist
  #Clean text
  texts = re.sub("USER", " ", text)
  texts = re.sub('RT[\s]+', '', texts)
  texts = re.sub("URL", " ", texts)
  texts = re.sub('[^a-zA-Z0-9]', " ", texts)
  text_clean = re.sub("(http[s]?\://\S+)|([\[\(].*[\)\]])|([#@]\S+)|\n", " ", texts)
  data['Tweet'] = data['Tweet'].apply(input_csv)
  #Insert new data to database
  query_text = "INSERT INTO Twitter_Tweets(Texts, Clean_Texts) values(?,?)"
  val = (text, text_clean)
  mycursor.execute(query_text, val)
  data_base.commit()
  print(text)
  print(text_clean)
  #API Response(s)
  json_response={
        'status_code': 200,
        'description': ("Texts are clean", "Data Successfully added"),
        'data': data,
    }
  response_data = jsonify(json_response)
  return  response_data
  

#error handler
@app.errorhandler(400)
def handle_400_error(_error):
  "the quest is halted, the fault is from you"
  return make_response(jsonify({'error':'Misunderstood'}), 400)

@app.errorhandler(401)
def handle_401_error(_error):
   "the quest is halted, it is unauthorized by the high council"
   return make_response(jsonify({'error':'Unauthorised'}), 401)

@app.errorhandler(404)
def handle_404_error(_error):
   "the quest is halted, there is no such quest"
   return make_response(jsonify({'error':'Not Found'}), 404)

@app.errorhandler(500)
def handle_500_error(_error):
   "the quest is halted, the high council is occupied at the moment"
   return make_response(jsonify({'error':'Server error'}), 500)  


if __name__ == '__main__':
    app.run(debug = True) #Run & Show Error (if any)