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
        datasets_array=[]
        for f in request.files.getlist('file'):
            datasets_array.append(f.filename) 
        # f.save(arg1 is the path, arg2 is the filename)
            print("Uploaded: "+f.filename,file=sys.stderr)
            f.save(os.path.join(app.config['UPLOAD_PATH'],  f.filename))
        return make_response(jsonify({"msg":"uploaded successfully","datasets_array":datasets_array}), 200)
#------------------------------------------------- Processing search-datasets request
@app.route('/search_datasets',methods=['POST','GET'])
def search_datasets_func():
    if(request.is_json):
        files = glob.glob('./upload/*')
        for f in files:
            os.remove(f)
        req=request.get_json();
        keywordlist=req.get("keywordlist")
        max_num=req.get("max_number")
        #max_num=5
        #keywordlist=["health","education"]
        #dictionary with datasetname as key and taglist as value {"datasetsname":[tag1,tag2]}
        datasets_with_tag_array={}
        # Dictionary to hold tags with keywords as keys
        dict_of_tags_basedon_keyword={}
        # ready for treemap; contains keyword as name and tags as children {"name"=keyword,"value"=75,children=[]} 
        keyword_and_tag_array=[]
        # To avoid duplicate tags;
        uniq_taglist=[]
        for keyword in keywordlist:
            # Temorporary array to hold the tags to use later on dictionary
            temp_array_for_tags_basedon_keyword=[]
            #array to hold dictionaries containing tag name and value [{"name":tagname, "value":25},{"name":tagname2, "value":25}]
            temp_dict_for_datasets_and_tag=[]
            # temoporay dictionary to hold name value and children
            temp_dict={}
            count=0
            # list that contains all the links from first page
            link_list=[]
            first_url="https://data.cityofnewyork.us/browse?amp=&q="+keyword+"&sortBy=relevance&page=1"
            link_list.append(first_url)
            paginationlink = requests.get(first_url)
            soup = BeautifulSoup(paginationlink.text, "html.parser")
            links=soup.findAll("a",{"class":"pageLink"})
            for link in links:
                link_list.append("https://data.cityofnewyork.us"+link['href'])
            print(link_list)
            for url in link_list:
                if(count<max_num):
                    datalink1="https://dev.socrata.com/foundry/data.cityofnewyork.us/"
                    datalink2='https://data.cityofnewyork.us/resource/'
                    response = requests.get(url)
                    soup = BeautifulSoup(response.text, "html.parser")
                    # parent div with meta tag
                    links=soup.findAll("div", {"class": "browse2-result"})
                    dict2={}
                    #print("url in link")
                if(count<max_num):
                    count2=0
                    for link in links:
                        tags_array=[]
                        array_to_contain_tag_dict=[]
                        if(count2<max_num):
                            try:
                                # get href and add .json at the end
                                href2=link.findAll("a",{"class":"browse2-result-api-link"})[0]["href"].replace(datalink1,datalink2)
                                href=href2+".json"
                                # Get the tags from here
                                #print("link is : ",href2)
                                title=link.findAll("a",{"class":"browse2-result-name-link"})[0].string
                                dict2[title]=href
                                taglist=link.findAll("div",{"class":"browse2-result-topics"})
                                tag_arr=taglist[0].findAll("a")
                                for tag_element in tag_arr:
                                    tag=tag_element.find("span").string
                                    tags_array.append(tag)
                                    if tag not in uniq_taglist:
                                        uniq_taglist.append(tag)
                                        temp_array_for_tags_basedon_keyword.append(tag)
                                        array_to_contain_tag_dict.append({"name":tag,"value":25})
                                datasets_with_tag_array[title]=tags_array
                                temp_dict_for_datasets_and_tag.extend(array_to_contain_tag_dict)
                                count2=count2+1
                            except IndexError:
                                pass
                                #print(link.findAll("a",{"class":"browse2-result-name-link"})[0].string)
                    #print(dict2)
                for key in dict2:
                    if(count<max_num):
                        try:
                            data=pd.read_json(dict2[key])
                            #print(key)
                            if not (os.path.exists("upload/"+re.sub("/","",key)+".csv")):
                                data.to_csv(r"upload/"+re.sub("/","",key)+".csv",sep=",",index=False)
                                count=count+1
                                print("fetched: ",count,"\n")
                        except:
                            print("error in file location")
            temp_dict["name"]=keyword
            temp_dict["value"]=75
            temp_dict["children"]=temp_dict_for_datasets_and_tag
            keyword_and_tag_array.append(temp_dict)
            #keyword_and_tag_array is for Treemap
            dict_of_tags_basedon_keyword[keyword]=temp_array_for_tags_basedon_keyword
        return make_response(jsonify({"keyword_and_tag_array":keyword_and_tag_array,"datasets_with_tag_array":datasets_with_tag_array,"dict_of_tags_basedon_keyword":dict_of_tags_basedon_keyword}), 200)
#------------------------------------------------- Processing first bar request
@app.route('/first_bar',methods=['POST','GET'])
def first_bar():
    if(request.is_json):
        req=request.get_json();
        if(req.get("type")=="uploaded"):
            mypath='./uploaded/*.csv'
        else:
            mypath='./upload/*.csv'
        dict1={}
        for filename in glob.glob(mypath):
            df = pd.read_csv(filename);
            fname=re.sub(r'.csv', '',filename[9:])
            for col in df.columns:
                if col not in dict1:
                    dict1[col]=1
                else:
                    dict1[col]=dict1[col]+1
        sorted_dict = sorted(dict1.items(), key=lambda x:x[1], reverse=True)
        dict3={}
        for a, b in sorted_dict: 
            dict3[a]=b
        dict4={"attributes":list(dict3.keys()),"frequency":list(dict3.values())}
        return make_response(jsonify(dict4), 200)
#------------------------------------------------- Processing process request
@app.route('/json',methods=['POST','GET'])
def hello_world2():
    if(request.is_json):
        req=request.get_json();
        datasets=req.get("datasets");
        #print("datasets are: ",req.get("all"), file=sys.stderr)
        if(req.get("myrequest")=='data'):
            datasets_with_Attributes={}
            count=0;
            type=req.get("type");
            if(type=="uploaded"):
                mypath='./uploaded/*.csv'
            else:
                mypath='./upload/*.csv'
            for filename in glob.glob(mypath):
                if(type!="uploaded" and req.get("all")=="false" ):
                    print("filename is: ",filename[9:], file=sys.stderr)
                    if(filename[9:] in datasets):
                        if(count<150):
                            count=count+1;
                            df = pd.read_csv(filename);
                            fname=re.sub(r'.csv', '',filename[9:])
                            datasets_with_Attributes[fname]=df.columns.tolist()
                elif(type=="uploaded"):
                    if(count<150):
                        count=count+1;
                        df = pd.read_csv(filename);
                        fname=re.sub(r'.csv', '',filename[11:])
                        datasets_with_Attributes[fname]=df.columns.tolist()
                elif(req.get("all")=="true"):
                    if(count<150):
                        count=count+1;
                        df = pd.read_csv(filename);
                        fname=re.sub(r'.csv', '',filename[9:])
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
            for key in sorted_Atrributes:
                # change here to set the number of times attributes occurs
                if(unionA[key]>2):
                    count2=count2+1;
                    #print("UnionA is ",key,unionA[key], file=sys.stderr)
                    #first_bar_dict[key]=unionA[key]
                    first_bar_values.insert(count2,unionA[key])
                    only_shared_attributes.insert(count2,key)
            # create the data for json reply
            first_bar_Arr.insert(0,only_shared_attributes)
            first_bar_Arr.insert(1,first_bar_values)
            mydata={"first_bar_Arr":first_bar_Arr,"unionA":unionA,"datasets_with_Attributes":datasets_with_Attributes,"sorted_Atrributes":sorted_Atrributes,"only_shared_attributes":only_shared_attributes}
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
                            print("Correlation: ",att)
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
            print("Kl_div got ",req.get("given"), file=sys.stderr)
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
# ---------------------------------------------------------------------------------------



#--------------------------------Main program starts here
if __name__ == '__main__':
   app.run(host='0.0.0.0')
   app.run(debug = True)
#--------------------------------


#https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#Preflighted_requests
