# -*- coding: utf-8 -*
import os
import time
import json
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from flask import render_template
from flask import Flask, request, abort
from flask_jsonpify import jsonify
from flask_cors import CORS
from neo4j import GraphDatabase
chrome_options = webdriver.ChromeOptions() 
chrome_options.add_argument('--headless') # 啟動無頭模式 
chrome_options.add_argument('--disable-gpu') # windows

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False
# driver = GraphDatabase.driver('bolt://4.tcp.ngrok.io:12329', auth=('neo4j', '12345'))

@app.route("/", methods=['GET'])
def hello():
    # GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', '12345'))
    return ("conntect to Neo4j")

@app.route("/graph", methods=['GET'])
def graph():
    return render_template("graph.html")

@app.route("/readme", methods=['GET'])
def readme():
    return render_template("information.html")

@app.route("/sub", methods=['GET'])
def sub():
    return render_template("sub.html")

@app.route("/sub", methods=['POST'])
def get_sublist():
    keyword_children = []
    data = request.get_json()
    sub = data['sub']
    for i in sub:
        get_sub(i,keyword_children)
    final_dict = {"name":"益生菌","children":keyword_children}
    # final_json = json.dumps(final_dict,ensure_ascii=False) 
    return final_dict

def get_sub(keyword,keyword_children):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless") #無頭模式
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)

    driver.get("http://www.google.com")
    input_element = driver.find_element_by_name("q")
    input_element.send_keys('益生菌'+keyword)
    time.sleep(2)
    # input_element.submit()
    htmltext = driver.page_source
    driver.close()
    return to_dict(keyword,htmltext,keyword_children)

def to_dict(keyword,htmltext,keyword_children):
    sub_children = []
    sub_name = {}
    soup = BeautifulSoup(htmltext, 'html.parser')
    for i in soup.find_all("div", class_="sbl1"):
        if len(i.get_text()) > 0:
            sub_name = {"name":i.get_text()}
            sub_children.append(sub_name)
    keyword_children.append({"name":keyword,"children":sub_children})
    return keyword_children

if __name__ == "__main__":
    app.run(debug=True)