import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import os as os
import pandas as pd
import re

def myscraper(url):
    datalink1="https://dev.socrata.com/foundry/data.cityofnewyork.us/"
    datalink2='https://data.cityofnewyork.us/resource/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    links=soup.findAll("div", {"class": "browse2-result"})
    dict2={}
    count=0
    for link in links:
        try:
            href=link.findAll("a",{"class":"browse2-result-api-link"})[0]["href"].replace(datalink1,datalink2)+".json"
            title=link.findAll("a",{"class":"browse2-result-name-link"})[0].string
            dict2[title]=href
            count=count+1
        except IndexError:
            pass
            #print(link.findAll("a",{"class":"browse2-result-name-link"})[0].string)
    print(count)
    for key in dict2:
        try:
            data=pd.read_json(dict2[key])
            print(key)
            data.to_csv(r"nyc/"+re.sub("/","",key)+".csv",sep="\t")
        except:
            print("error in file location")
myurl =['https://data.cityofnewyork.us/browse?amp=&q=education&sortBy=relevance&page=8','https://data.cityofnewyork.us/browse?amp=&q=education&sortBy=relevance&page=9']
for url in myurl:
    myscraper(url)