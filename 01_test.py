# chmod 644 01_test.py
from flask import Flask, render_template, request
import os,glob,sys
import os.path
from os import path
import re
import json
from flask import jsonify, make_response
import pandas as pd
import numpy as np
from sklearn.feature_selection import VarianceThreshold
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
from sklearn.feature_selection import SelectKBest, SelectPercentile
from flask_cors import CORS
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
from flask import send_file
import time
app = Flask(__name__)
CORS(app)
dict_to_hold_download_link={}
#--------------------------------------------------------------------------------------------------------------------------------------------------- Merge datasets
@app.route('/merge',methods=['POST','GET'])
def merge_datasets():
    if(request.is_json):
        req=request.get_json();
        datasets_array=req.get("clicked_datasets_with_link")
        df_array=[]
        for dataset in datasets_array:
            dfname=pd.read_csv(dataset+".csv")
            df_array.append(dfname)
        merged=pd.concat(df_array)
        merged.to_csv('merged/export.csv',sep=",",index=False)
        print("datasets are: ",datasets_array, file=sys.stderr)
        response=make_response(jsonify({"response":"Done"}), 200)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response;
#--------------------------------------------------------------------------------------------------------------------------------------------------- Return to Download
@app.route('/returnfiles')
def return_files_tut():
    return send_file('merged/export.csv', attachment_filename='export.csv',as_attachment=True)
# ---------------------------------------------------------------------------------------Return Manual
@app.route('/returnpdf')
def return_files_tut2():
    return send_file('uploaded/urbanForestManual.pdf', attachment_filename='urbanForestManual.pdf',as_attachment=True)
#--------------------------------Main program starts here
if __name__ == '__main__':
   app.run(host='0.0.0.0')
   app.run(debug = True)
#--------------------------------


#https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#Preflighted_requests
