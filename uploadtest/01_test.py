# chmod 644 01_test.py
from flask import Flask, render_template, request
from werkzeug import secure_filename
import os,glob,sys
import re
import json
from flask import jsonify, make_response
import pandas as pd
from sklearn.feature_selection import VarianceThreshold
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
#------------------------------------------------- Uploads are handled here
# This is where we set the path
app.config['UPLOAD_PATH']="./upload"
@app.route('/upload')
def upload_file1():
   return render_template('upload.html')
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      files = glob.glob('./upload/*')
      for f in files:
         os.remove(f)
# request.files conatains (werkzeug.datastructures.FileStorage)  
      for f in request.files.getlist('file'): 
# f.save(arg1 is the path, arg2 is the filename)
         print(f.filename)
         f.save(os.path.join(app.config['UPLOAD_PATH'],  secure_filename(f.filename)))
      return 'file uploaded successfully'
#------------------------------------------------- Processing probability distribution request
@app.route('/json2',methods=['POST','GET'])
def hello_world3():
    if(request.is_json):
        req=request.get_json();
        if(req.get("datasets")!=''):
            datasets=req.get("datasets")
            result={}
            for dataset in datasets:
                dataset_name=dataset+".csv";
                data=pd.read_csv(dataset_name)
                newData={}
                for i in data:
                    len=data[i].size
                    dict_test=[]
                    newData[i]=data[i].value_counts().to_dict()
                    for j in newData[i]:
                        p=newData[i][j]/len
                        if(p!=0):
                            print("P is: ",i,p, file=sys.stderr)
                            dict_test.append(round(p,4))
                    newData[i]=dict_test
                result[dataset]=newData
        for i in result:
            print("Result is: ",i, file=sys.stderr)
        return make_response(jsonify(result), 200)
#------------------------------------------------- Processing other request
@app.route('/json',methods=['POST','GET'])
def hello_world2():
    if(request.is_json):
        req=request.get_json();
        if(req.get("myrequest")=='data'):
            datasets_with_Attributes={}
            count=0;
            max=150;
            for filename in glob.glob('./upload/*.csv'):
                count=count+1;
                if(count<max):
                    df = pd.read_csv(filename);
                    fname=re.sub(r'.csv', '',filename[9:])
                    datasets_with_Attributes[fname]=df.columns.str.lower().tolist()
            unionA={}
            for key in datasets_with_Attributes:
                for val in datasets_with_Attributes[key]:
                    if val not in unionA:
                        unionA[val]=1;
                    else:
                        unionA[val]=unionA[val]+1;
            sorted_Atrributes = sorted(unionA, key=unionA.get, reverse=True)
            only_shared_attributes=[];
            count=0
            for key in sorted_Atrributes:
                if(unionA[key]>1):
                    count=count+1;
                    only_shared_attributes.insert(count,key)
            # create the data for json reply
            mydata={"unionA":unionA,"datasets_with_Attributes":datasets_with_Attributes,"sorted_Atrributes":sorted_Atrributes,"only_shared_attributes":only_shared_attributes}
            #print("json is: ",mydata, file=sys.stderr)
            return make_response(jsonify(mydata), 200)
        elif(req.get("filename")!=''):
            file =req.get("filename")
            data=pd.read_csv(file)
            dict1={}
            dict2=[]
            count=0;
            dict1["number_of_rows"]=data.shape[0];
            dict1["number_of_columns"]=data.shape[1];
            for columns in data.columns:
                count=count+1
                dict2.insert(count,columns);
            dict1["attributes"]=dict2
            return make_response(jsonify(dict1), 200)
    else:
        return make_response(jsonify({"message": "Else"}), 200)

@app.route('/stat_metrics',methods=['POST','GET'])
def stat_metric():
    print("Hello")


def process_data():
    # datasets_with_Attributes starts here
    datasets_with_Attributes={}
    for filename in glob.glob('*.csv'):
        df = pd.read_csv(filename)
        fname=re.sub(r'.csv', '',filename)
        datasets_with_Attributes[fname]=df.columns.str.lower().tolist()
    unionA={}
    for key in datasets_with_Attributes:
        for val in datasets_with_Attributes[key]:
            if val not in unionA:
                unionA[val]=1
            else:
                unionA[val]=unionA[val]+1
    sorted_Atrributes = sorted(unionA, key=unionA.get, reverse=True)
    # return only shared attrbutes
    only_shared_attributes=[]
    count=0
    for key in sorted_Atrributes:
        if(unionA[key]>1):
            count=count+1
            only_shared_attributes.insert(count,key)
    # create the data for json reply
    mydata={"unionA":unionA,"datasets_with_Attributes":datasets_with_Attributes,"sorted_Atrributes":sorted_Atrributes,"only_shared_attributes":only_shared_attributes}
    return mydata
def pr():
    return {"hi":"data1"}


#--------------------------------Main program starts here
if __name__ == '__main__':
   app.run(host='0.0.0.0')
   app.run(debug = True)
#--------------------------------


#https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#Preflighted_requests
