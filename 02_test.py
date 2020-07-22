# chmod 644 01_test.py
from flask import Flask, render_template, request
from werkzeug import secure_filename
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
        datasets_array=req.get("dataset_array_to_merge")
        mypath='upload/*.csv'
        datasets_array=datasets_array
        df_array=[]
        for filename in glob.glob(mypath):
            filename=filename[7:]
            if filename in datasets_array:
                dfname=filename[0:-4]
                dfname=pd.read_csv("upload/"+filename)
                df_array.append(dfname)
        merged=pd.concat(df_array)
        merged.to_csv('upload/export.csv',sep=",",index=False)
        response=make_response(jsonify({"response":"Done"}), 200)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response;
#--------------------------------------------------------------------------------------------------------------------------------------------------- Return to Download
@app.route('/returnfiles')
def return_files_tut():
    return send_file('upload/export.csv', attachment_filename='export.csv',as_attachment=True)
# ---------------------------------------------------------------------------------------Return Manual
@app.route('/returnpdf')
def return_files_tut2():
    return send_file('uploaded/urbanForestManual.pdf', attachment_filename='urbanForestManual.pdf',as_attachment=True)

#--------------------------------------------------------------------------------------------------------------------------------------------------- Processing search-datasets request
@app.route('/search_datasets',methods=['POST','GET'])
def search_datasets_func():
    global dict_to_hold_download_link
    if(request.is_json):
        req=request.get_json();
        keyword_list=req.get("keywordlist")
        max_num=req.get("max_number")
        start=time.time()
        max_num2=max_num+10 # we are fetching 10 extra datasets so that if links are not dataset
        datasets_with_tag_array={}
        dict_of_tags_basedon_keyword={}
        keyword_based_datasetname_array={}
        #keyword_list=['health','energy','education']
        files = glob.glob('./upload/*')
        for f in files:
            os.remove(f)
        for keyword in keyword_list:
            print("Fetching ...",keyword)
            temp_list_for_tags=[]
            temp_list_for_datasets=[]
            url = 'http://api.us.socrata.com/api/catalog/v1?q='+keyword+'&domains=data.cityofnewyork.us&offset=0&limit='+str(max_num2)
            resp = requests.get(url=url)
            data = resp.json()
            tags_dict={}
            for i in data['results']:
                if len(temp_list_for_datasets)<max_num and i['resource']['type']=='dataset':
                    datasetname=re.sub("/","",i['resource']['name'])
                    dataset_id=i['resource']['id']
                    try:
                        url2='https://data.cityofnewyork.us/resource/'+dataset_id+".csv"
                        dict_to_hold_download_link[datasetname]=url2
                        #data=pd.read_csv(url2)
                        #data.to_csv("./upload/"+datasetname+".csv",sep=",",index=False)
                        datasets_with_tag_array[datasetname]=i['classification']['domain_tags']
                        temp_list_for_tags+=i['classification']['domain_tags']
                        tags_dict[datasetname]=i['classification']['domain_tags']
                        temp_list_for_datasets.append(datasetname)
                        #print("Found :",i['resource']['type'],dataset_id)
                    except:
                        print("Error :",i['resource']['type'],datasetname)
                        #data.to_csv("./upload/"+i['resource']['name']+".csv")
            dict_of_tags_basedon_keyword[keyword]=temp_list_for_tags
            uniq=[]
            for key in dict_of_tags_basedon_keyword:
                temp=[]
                for tag in dict_of_tags_basedon_keyword[key]:
                    if tag not in uniq:
                        temp.append(tag)
                        uniq.append(tag)
                    else:
                        pass
                dict_of_tags_basedon_keyword[key]=temp
            keyword_based_datasetname_array[keyword]=temp_list_for_datasets
        print("Elapsed time: ",time.time()-start)
        return make_response(jsonify({
            "datasets_with_tag_array":datasets_with_tag_array,
            "dict_of_tags_basedon_keyword":dict_of_tags_basedon_keyword,
            "keyword_based_datasetname_array":keyword_based_datasetname_array}), 200)
#--------------------------------------------------------------------------------------------------------------------------------------------------- Downloading datasets after search-datasets request
@app.route('/dataset_loader',methods=['POST','GET'])
def load_all():
    print("Got it")
    start=time.time()
    global dict_to_hold_download_link
    for key in dict_to_hold_download_link:
        try:
            data=pd.read_csv(dict_to_hold_download_link[key])
            data.to_csv(r"upload/"+re.sub("/","",key)+".csv",sep=",",index=False)
        except:
            print("error in file location")
    print("Elapsed Time is: ",time.time() - start)
    return make_response(jsonify({"Download status":"Downloadin is done!"}), 200)

#--------------------------------------------------------------------------------------------------------------------------------------------------- Processing showlink request
@app.route('/showlink_processor',methods=['POST','GET'])
def processing():
    if(request.is_json):
        req=request.get_json();
        datasets=req.get("datasets");
        #print("datasets are: ",req.get("all"), file=sys.stderr)
        if(req.get("myrequest")=='data'):
            datasets_with_Attributes={}
            count=0;
            type=req.get("type");
            if(type=="first_load"):
                mypath='./uploaded/*.csv'
            else:
                mypath='./upload/*.csv'
            for filename in glob.glob(mypath):
                if(type!="first_load" and req.get("all")=="false" ):              #--------------------------- executed after uploaded is done
                    if(filename[9:] in datasets):
                        if(count<150):
                            count=count+1;
                            df = pd.read_csv(filename);
                            fname=re.sub(r'.csv', '',filename[9:])
                            datasets_with_Attributes[fname]=df.columns.tolist()
                elif(type=="first_load"):                                        #--------------------------- executed after uploaded is done
                    if(count<150):
                        count=count+1;
                        df = pd.read_csv(filename);
                        fname=re.sub(r'.csv', '',filename[11:])
                        datasets_with_Attributes[fname]=df.columns.tolist()
            unionA={}
            for key in datasets_with_Attributes:
                for val in datasets_with_Attributes[key]:
                    if val not in unionA:
                        unionA[val]=1;
                    else:
                        unionA[val]=unionA[val]+1;
            sorted_Atrributes = sorted(unionA, key=unionA.get, reverse=True)
            only_shared_attributes=[];
            count2=0
            first_bar_Arr=[]
            first_bar_values=[]
            min_occurence=3;
            for key in sorted_Atrributes:
                # change here to set the number of times attributes occurs
                if(unionA[key]>=min_occurence):
                    count2=count2+1;
                    first_bar_values.insert(count2,unionA[key])
                    only_shared_attributes.insert(count2,key)
            # get the datasets with above occurence condition
            temp_arr=[] # this is to use next to avoid dataset repeatation
            temp_dic={} # temp dic is for new datasets_with_Attributes
            for attr in only_shared_attributes:
                for dataset in datasets_with_Attributes:
                    if attr in datasets_with_Attributes[dataset]:
                        if dataset not in temp_arr:
                            temp_arr.append(dataset)
                            temp_dic[dataset]=datasets_with_Attributes[dataset]
            # create the data for json reply
            first_bar_Arr.insert(0,only_shared_attributes)
            first_bar_Arr.insert(1,first_bar_values)
            mydata={"first_bar_Arr":first_bar_Arr,"unionA":unionA,"datasets_with_Attributes":temp_dic,"sorted_Atrributes":sorted_Atrributes,"only_shared_attributes":only_shared_attributes}
            #print("json is: ",mydata, file=sys.stderr)
            return make_response(jsonify(mydata), 200)
        elif(req.get("filename")!=''):
            file =req.get("filename")
            data=pd.read_csv(file)
            dict1={}
            dict2=[]
            count3=0;
            dict1["number_of_rows"]=data.shape[0];
            dict1["number_of_columns"]=data.shape[1];
            for columns in data.columns:
                count3=count3+1
                dict2.insert(count3,columns);
            dict1["attributes"]=dict2
            return make_response(jsonify(dict1), 200)
    else:
        return make_response(jsonify({"message": "Else"}), 200)

#--------------------------------------------------------------------------------------------------------------------------------------------------- Processing probability distribution request
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
                            dict_test.append(round(p,4))
                    newData[i]=dict_test
                result[dataset]=newData
        return make_response(jsonify(result), 200)
#--------------------------------------------------------------------- Processing stat request
@app.route('/statmetrics',methods=['POST','GET'])
def stat_metric():
    if(request.is_json):
        req=request.get_json();
# --------------------------------------------Prob distribution
        if(req.get("req_for")=='prob_dist'):
            given=req.get("given")
            dict={}
            for dataset in given[0]:
                dataset2="./upload/"+dataset+".csv"
                data=pd.read_csv(dataset2)
                data=data.dropna(how='all',axis='columns')
                data=data.dropna(how='all',axis='rows')
                data=data.fillna(value=0)
                total=data.shape[0]
                dict3={}
                for col in data.columns:
                    if col in given[1]:
                        dict2={} 
                        uniq=data[col].unique()
                        for i in uniq:
                            dict2[str(i)]=data.loc[data[col]==i].shape[0]
                            #print(i,data.loc[data[col]==i].shape[0]/total)
                        dict3[col]=dict2
                dict[dataset]=dict3
            return make_response(jsonify({"prob_data":dict}), 200)
# --------------------------------------------Correlation
        elif(req.get("req_for")=='correlation'):
            #print("data is ",req.get("given"), file=sys.stderr)
            corr_dict={}
            given=req.get("given")
            numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
            for dataset in given[0]:
                dataset2="./upload/"+dataset+".csv"
                if(path.exists(dataset2)):
                    data=pd.read_csv(dataset2)
                    numerical_vars = list(data.select_dtypes(include=numerics).columns)
                    data = data[numerical_vars]
                    data=data.dropna(how='all',axis='columns')
                    data=data.dropna(how='all',axis='rows')
                    data=data.fillna(value=0)
                    dict2={}
                    for att in given[1]:
                        if att in data.columns:
                            
                            dict2[att]=data.corr()[att].drop(att,axis=0).to_dict()
                    corr_dict[dataset]=dict2
                            #print("data is ",corr_dict, file=sys.stderr)
            return make_response(jsonify({"correlation_data":corr_dict}), 200)
# --------------------------------------------KL-Divergnce
        elif(req.get("req_for")=='kl_div'):
            #print("Kl_div got ",req.get("given"), file=sys.stderr)
            kl_dict={}
            given=req.get("given")
            numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
            for dataset in given[0]:
                dataset2="./upload/"+dataset+".csv"
                if(path.exists(dataset2)):
                    data=pd.read_csv(dataset2)
                numerical_vars = list(data.select_dtypes(include=numerics).columns)
                data = data[numerical_vars]
                data=data.dropna(how='all',axis='columns')
                data=data.dropna(how='all',axis='rows')
                data=data.fillna(value=0)
                att1_dict={}
                for att in given[1]:
                    if(att in data.columns):
                        att2_dict={}
                        for att2 in data.columns:
                            p=data[att]
                            q=data[att2]
                            kl_val=np.sum(np.where(p != 0, p * np.log(p / q), 0))
                            if(np.isnan(kl_val)):
                                print("Null value is in dataset: ",dataset2,"Attribute :",att2," : ",kl_val,"\n")
                            else:
                                if((kl_val!=np.inf)):
                                    att2_dict[att2]=kl_val
                        att1_dict[att]=att2_dict
                kl_dict[dataset]=att1_dict 
            return make_response(jsonify({"kl_data":kl_dict}), 200)
        return make_response(jsonify({"else":"something wrong"}), 200)
    else:
        return make_response(jsonify({"message": "Else"}), 200)
#--------------------------------------------------------------------- Processing stat request for uploaded
@app.route('/statmetrics2',methods=['POST','GET'])
def stat_metric2():
    if(request.is_json):
        req=request.get_json();
# ------------------------------------------------------------Prob distribution
        if(req.get("req_for")=='prob_dist'):
            given=req.get("given")
            dict={}
            for dataset in given[0]:
                dataset2="./uploaded/"+dataset+".csv"
                data=pd.read_csv(dataset2)
                data=data.dropna(how='all',axis='columns')
                data=data.dropna(how='all',axis='rows')
                data=data.fillna(value=0)
                total=data.shape[0]
                dict3={}
                for col in data.columns:
                    if col in given[1]:
                        dict2={} 
                        uniq=data[col].unique()
                        for i in uniq:
                            dict2[str(i)]=data.loc[data[col]==i].shape[0]
                            #print(i,data.loc[data[col]==i].shape[0]/total)
                        dict3[col]=dict2
                dict[dataset]=dict3
            return make_response(jsonify({"prob_data":dict}), 200)
# ---------------------------------------------------------------------------------------Correlation
        elif(req.get("req_for")=='correlation'):
            #print("data is ",req.get("given"), file=sys.stderr)
            corr_dict={}
            given=req.get("given")
            numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
            for dataset in given[0]:
                dataset2="./uploaded/"+dataset+".csv"
                if(path.exists(dataset2)):
                    data=pd.read_csv(dataset2)
                    numerical_vars = list(data.select_dtypes(include=numerics).columns)
                    data = data[numerical_vars]
                    data=data.dropna(how='all',axis='columns')
                    data=data.dropna(how='all',axis='rows')
                    data=data.fillna(value=0)
                    dict2={}
                    for att in given[1]:
                        if att in data.columns:
                            #print("Correlation: ","dataset is: ",dataset," and attribute: ",att)
                            dict2[att]=data.corr()[att].drop(att,axis=0).to_dict()
                    corr_dict[dataset]=dict2
                            #print("data is ",corr_dict, file=sys.stderr)
            return make_response(jsonify({"correlation_data":corr_dict}), 200)
# ---------------------------------------------------------------------------------------KL-Divergnce
        elif(req.get("req_for")=='kl_div'):
            
            kl_dict={}
            given=req.get("given")
            numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
            for dataset in given[0]:
                dataset2="./uploaded/"+dataset+".csv"
                if(path.exists(dataset2)):
                    data=pd.read_csv(dataset2)
                numerical_vars = list(data.select_dtypes(include=numerics).columns)
                data = data[numerical_vars]
                data=data.dropna(how='all',axis='columns')
                data=data.dropna(how='all',axis='rows')
                data=data.fillna(value=0)
                att1_dict={}
                for att in given[1]:
                    if(att in data.columns):
                        att2_dict={}
                        for att2 in data.columns:
                            p=data[att]
                            q=data[att2]
                            kl_val=np.sum(np.where(p != 0, p * np.log(p / q), 0))
                            if(np.isnan(kl_val)):
                                pass
                                #print("Kl_divergence: ","dataset: ",dataset," Attribute: ",att2,kl_val)
                            else:
                                if((kl_val!=np.inf)):
                                    att2_dict[att2]=kl_val
                        att1_dict[att]=att2_dict
                kl_dict[dataset]=att1_dict 
            return make_response(jsonify({"kl_data":kl_dict}), 200)
        return make_response(jsonify({"else":"something wrong"}), 200)
    else:
        return make_response(jsonify({"message": "Else"}), 200)
#--------------------------------Main program starts here
if __name__ == '__main__':
   app.run(host='0.0.0.0')
   app.run(debug = True)
#--------------------------------


#https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#Preflighted_requests
