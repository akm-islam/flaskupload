from flask import Flask
from flask import request
from flask import jsonify, make_response, sys, os, 
import pandas as pd
import numpy as np
from flask_cors import CORS
# ----------------------------> All imports end here
flag='Test'
app = Flask(__name__)
CORS(app)
@app.route("/json", methods=["POST"])
def json_example():
    return make_response(jsonify({"message": "Request body must be JSON"}), 400)
#----------------------------------------------------------------------------------------> Get Request
@app.route("/get",methods=["GET"])
def get_example():
    return "Hello GET"
#----------------------------------------------------------------------------------------> Get/POST Request
@app.route('/form-example', methods=['GET', 'POST']) #allow both GET and POST requests
def form_example():
    if request.method == 'POST': #this block is only entered when the form is submitted
        #prints the values of form as a dictionary
        print(request.form, file=sys.stderr)
    return '''<form method="POST">
                  Language: <input type="text" name="language"><br>
                  Framework: <input type="text" name="framework"><br>
                  <input type="submit" value="Submit"><br>
              </form>'''
if __name__ == '__main__':
    app.run(host = '192.168.1.114',port='5006')
    app.run(debug=True)
    

