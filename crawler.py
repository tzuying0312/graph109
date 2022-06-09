import re
import os
import csv
import time
import json
import jieba
import requests
import warnings
import numpy as np
import pandas as pd
import jieba.posseg as pseg
from os import system, name  
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup
from readability import Document
from threading import Thread
import math, sys, time, random, collections
requests.packages.urllib3.disable_warnings()
from fake_useragent import UserAgent
ua = UserAgent()
jieba.setLogLevel(20)

href_list = []
url_rank_page = {}
stopWords = ['\t',' ','【','】','⭐','『','』','\u3000','.','🔔','\r\n']
corpus_file_list = ['google_tw_益生菌.csv','add_word.csv','stopwords.txt','trash.txt']

shop_url = ['http://www.asanga.com.tw/single.php?ProductID=21&lang=zh','https://www.biomedimei.com/collections/%E7%9B%8A%E7%94%9F%E8%8F%8C','https://www.doterra.com/TW/zh_TW/p/pb-assist-jr',
'https://www.orchid-city.com/products/%E8%98%AD%E9%83%BD%E3%82%BB%E3%83%83%E3%82%B3%E3%82%AF-%E7%9B%8A%E7%94%9F%E8%8F%8C','https://www.nutrimate.com.tw/products/products/itemlist/category/116.html']

need_url = ['https://askthescientists.com/zh-hant/qa/usana-probiotic/','https://www.edh.tw/media_article/536','https://www.kskhealth.com/pages/probiotics','https://www.kskhealth.com/pages/probiotics-recommend',
'http://www.newbellus.com.tw/index.php?temp=prm&lang=cht','https://www.longwalk-biotech.com.tw/pages/probiotics-sales-10','https://www.kskhealth.com/pages/2020-probiotics-recommend']

way_two_url = ['https://www.tklab.com.tw/pages/functional-food-probiotics','https://www.kskhealth.com/pages/2020-probiotics-recommend',
'https://www.edh.tw/media_article/536','http://www.newbellus.com.tw/index.php?temp=prm&lang=cht','https://www.kskhealth.com/pages/probiotics']


for corpus_file in corpus_file_list:
    with open('lib/corpus/'+corpus_file,'r',encoding='utf-8')as myfile: 
        if 'csv' in corpus_file:
            data = csv.DictReader(myfile)
            for row in data:
                jieba.add_word(row['Keyword'],None,'n')
        else:
            for data in myfile.readlines():
                data = data.strip()
                stopWords.append(data)

def load_data(filename):
    try:   
        with open('lib/json/'+filename+'.json',encoding='utf-8') as json_file: 
            file_dict = json.load(json_file) 
    except:
        file_dict = {}
    return file_dict

def get_table_to_corpus():
    with open('lib/corpus/table.txt','r',encoding='utf-8') as in_file:
        for word in in_file:
            jieba.add_word(word.replace('\n',''),None,'n')

def request_soup(url,opt,headers = None, rank_page = None):
    need_continue = True
    while need_continue == True:
        try:
            res = requests.get(url,verify=False,headers=headers)
            if res.apparent_encoding == 'Windows-1254':
                pass
            else :
                res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text,"lxml")
            if 'IP address' in soup.get_text():
                tfidf_log('connect','Connection refused...')
                # print('Connection refused...')
                int('error')
            need_continue = False
            if opt == 'google':      
                href = soup.find_all('div',class_='ZINbbc xpd O9g5cc uUPGi')
                for a in href:
                    j = a.find('a')
                    url = j.get('href')
                    if ("url?q=http" in url) and ("https://www.youtube.com/" not in url) :
                        try : 
                            url = url.split('&')[0][7:]
                            url = url.replace("%25",'%').replace('%3F','?').replace('%3D','=').replace('%26','&').replace('%2B','+')
                            # if url in shop_url :
                            #     pass
                            # elif ('shop' in url or 'product' in url or 'carrefour' in url or 'pchome' in url or 'costco' in url or 'watsons' in url or 'etmall' in url or 'buy123' in url or 'twgreengold' in url or 'gnc' in url or 'vilson' in url or 'leezen' in url or 'mall.yahoo' in url or 'greencome' in url or 'rakuten' in url or 'vivatv' in url) and (url not in need_url):
                            #     pass
                            # else:
                            href_list.append(url)
                            url_rank_page.setdefault(url,rank_page+1)
                            # tfidf_log('info',{url:str(rank_page+1)})
                        except:
                            tfidf_log('error','google page error')
                            # print('error !!!')
                return href_list
                    
            elif opt == 'div':
                try:
                    del_tag_list = ['footer','header','sidebar','navbar','privacy','sidebar','menu','menu-label','menu-item','terms']
                    del_list = ['footer','header','aside','nav','script','meta','style','noscript']
                    clean_soup = clean(url,res,soup,del_list,del_tag_list)
                    # div = clean_soup.find('div')
                    return clean_soup.get_text(),clean_soup
                except Exception as e:
                    pass
                    # tfidf_log('error',{'clean_soup':e})
                    # print(e)

            else :
                try:
                    result_stats = soup.find('div',id = 'result-stats')
                    return int(result_stats.text.split('項')[0][2:].replace(',',''))
                except Exception as e:
                    tfidf_log('error',{'result_stats':e})
                # pass   
        except Exception as e:
            tfidf_log('error',e)
            time.sleep(5)
            if name == 'nt': 
                os.system('rasdial.exe /disconnect')
            else: 
                _ = system('scutil --nc stop PPPoE')

            time.sleep(5)

            if name == 'nt': 
                os.system('rasdial 寬頻連線 75952444@hinet.net qjtwhkbb')
        
            else : 
                _ = system('scutil --nc start PPPoE')

            time.sleep(5)
            # print('Try again now...')

def clean(url,res,soup,del_list,del_tag_list):
    tfidf_log('url',url)
    web_soup = BeautifulSoup(res.text,"lxml")
    # clean_soup = way_two(url,web_soup,del_list,del_tag_list)
    div = web_soup.find('div') 
    doc = Document(res.text)
    if len(BeautifulSoup(doc.summary(),"lxml").text) > len(div.get_text())*0.85 and url not in way_two_url and 'dietician.com' not in url and 'kskhealth.com' not in url:
        first_soup = BeautifulSoup(doc.summary(),"lxml")
#         如果內文<100個文字猜測是購物網站
        if len(first_soup.get_text()) < 100 and url not in need_url:
            tfidf_log('type','購物網站')
            return None
        else:
            clean_soup = way_two(url,first_soup,del_list,del_tag_list)            
    else:
        clean_soup = way_two(url,web_soup,del_list,del_tag_list)
    return clean_soup

def way_two(url,soup_temp,del_list,del_tag_list):
    [del_text.extract() for del_text in soup_temp(del_list)]
    for del_word in del_tag_list:
        for tag in soup_temp.find_all('div',{'id':True}):
            if fuzz.ratio(tag['id'],del_word)>80:
                soup_temp.find('div',id = tag['id']).extract()
            else:
                continue
        for element in soup_temp.find_all(class_=True):
            for text in element['class']:
                try:
                    if fuzz.ratio(text,del_word)>90:
                        soup_temp.find(class_ = element['class']).extract()
                except AttributeError:
                    pass
    if url in need_url:
        final_soup_temp = soup_temp
    else:
        final_soup_temp = tell_shop(soup_temp)
    return final_soup_temp

def tell_shop(soup_temp):
    shop_tag = ['購物車','購物金','立即購買','立即訂購']
    for tag in shop_tag:
        if(tag in str(soup_temp.get_text)):
            tfidf_log('tag',tag)
            return None
        else:
            return soup_temp

def user_keyword(key,page):
    key = key.replace(' ','+')
    web_page = (int(page)-1)//10
    page = int(page) - (web_page*10)
    
    for i in range(0,web_page+1):
        google_url = 'https://www.google.com/search?q='+key+'&start='+str(i*10)
        href_list = request_soup(google_url,'google',None,i)
    final_href_list = href_list[:web_page*10+page] 
    start_get_html(final_href_list,key)

def start_get_html(final_href_list,key):
    # tfidf_log(str(article+1),final_href_list[article])
    # remainderWords(article,final_href_list[article],key)
    tfidf_log('info',final_href_list)
    url_del = ['carrefour','gnc','vilson','leezen','mall.yahoo','greencome','eshop','ftvmall','maoup.com','dradvice','books.com','jpmed.com'\
    ,'rakuten','vivatv','pchome','costco','watsons','etmall','buy123','twgreengold','shopping.friday','momoshop','tw.shop','vilson','shopee.tw','pandababy.com.tw/SalePage',
    'www.dahuei.com/products/']

    for article,url in enumerate(final_href_list):    
        if any(url_del_tag in url for url_del_tag in url_del) or url in shop_url:
            tfidf_log('article',str(article+1))
            tfidf_log('url',url)
            tfidf_log('type','購物網站')
        else:
            remainderWords(article,url,key)
        
def remainderWords (article,url,key): 
    start_time = time.perf_counter()
    pseg_word_list = []
    pseg_dict = {}
    tfidf_log('article',str(article+1))
    # headers = {'User-Agent': ua.random}   
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    div_word = request_soup(url,'div',headers)
    try:
        web_soup = div_word[1]
        # print(web_soup)
        div_word = div_word[0]
        tfidf_log('len',str(len(div_word)))
        # for tr in web_soup.find_all('tr'):
        #     td = tr.find('td')
        #     try :     
        #         with open('lib/corpus/table.txt','a',encoding='utf-8') as in_file:
        #             in_file.write(td.text.replace('\n','')+'\n')
        #     except:
        #         continue
        get_table_to_corpus()
        # segments = jieba.cut(div_word)
        segments = pseg.cut(div_word)
        for w in segments:
            if w.flag == 'nr' or w.flag == 's' or w.flag == 'ns' or w.flag == 'nz' or w.flag == 'nt' or w.flag == 'nw' or w.flag == 'nrt':
                pseg_dict.setdefault(w.word,'n')
            elif w.flag == 'b' or w.flag == 'an' or w.flag == 'ad' or w.flag == 'z':
                pseg_dict.setdefault(w.word,'a')
            elif w.flag == 'vn' or w.flag == 'vd' or w.flag == 'f':
                pseg_dict.setdefault(w.word,'v')
            elif w.flag == 't':
                pseg_dict.setdefault(w.word,'d')
            else:
                pseg_dict.setdefault(w.word,w.flag)
            pseg_word_list.append(w.word)
        
        # remainderWords = list(filter(lambda a: a not in stopWords and a != '\n' and len(a)>1 ,segments))
        remainderWords = list(filter(lambda a: a not in stopWords and a != '\n' and len(a)>1 ,pseg_word_list))
        tfidf(article,remainderWords,web_soup,key,start_time,pseg_dict,url)
    except Exception as e:
        # pass
        tfidf_log('remainderWords',e)

def tfidf(article,remainderWords,web_soup,key,start_time,pseg_dict,url):
    
    DF = {}
    summary_dict = {}
    summary_list = []
    idf_d_dict = load_data('idf_d')
    ngd_dict = load_data('ngd')
    idf_u_url = 'https://www.google.com/search?q='+key
    # headers = {'User-Agent': ua.random}
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    idf_u = request_soup(idf_u_url,'idf_u',headers)

    for i in range(len(remainderWords)):
        tokens = remainderWords[i]
        try:
            DF[tokens].add(i)
        except:
            DF[tokens] = {i}

    for i in DF:
        DF[i] = len(DF[i])
    # count_word(DF)

    for i in DF:
        if DF[i]>3 or '菌' in i or '推薦' in i or '益生' in i: 
            try:
                i = i.replace(' ','+')
                idf_d_url = 'https://www.google.com/search?q='+key+'+intext%3A"'+i+'"'
                # headers = {'User-Agent': ua.random}
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                idf_d = dict_data(i,idf_d_dict)
                if idf_d == '':
                    idf_d = request_soup(idf_d_url,'idf_d',headers)
                    if idf_d != None:
                        idf_d_dict.setdefault(i,idf_d)
                    time.sleep(1)
                tf = DF[i]/len(remainderWords)
                idf = np.log(idf_u/(idf_d+1))
                # ngd1 = NGD('功效',i,ngd_dict,idf_d)
                # ngd2 = NGD('品牌',i,ngd_dict,idf_d)
                # ngd3 = NGD('菌種',i,ngd_dict,idf_d)
                # ngd4 = NGD('器官',i,ngd_dict,idf_d)
                # ngd5 = NGD('對象',i,ngd_dict,idf_d)
                # ngd6 = NGD('挑選原則',i,ngd_dict,idf_d)

                try :
                    # summary_dict = {"rank_page":url_rank_page[url],"word": i,'tf': tf,"idf":idf,"tfidf":tf*idf,"count":DF[i],"pos":pseg_dict[i],'ngd功效':ngd1,'ngd品牌':ngd2,'ngd菌種':ngd3,'ngd器官':ngd4,'ngd對象':ngd5,'ngd挑選原則':ngd6}
                    summary_dict = {"rank_page":url_rank_page[url],"word": i,'tf': tf,"idf":idf,"tfidf":tf*idf,"count":DF[i]}
                except :
                    summary_dict = {"word": i,'tf': tf,"idf":idf,"tfidf":tf*idf,"count":DF[i]}

                tfidf_log('complete',summary_dict)
                # print(summary_dict)
                summary_list.append(summary_dict)
            except Exception as e:
                tfidf_log('error',{i:e})
                # print(i,e)

    # print('DONE:tfidf')  
    summary_df = pd.DataFrame(summary_list) 
    try:
        update_dict('idf_d',idf_d_dict)
        update_dict('ngd',ngd_dict)
        # summary_df = summary_df[summary_df['tfidf'] > summary_df.tfidf.quantile([0.5]).values[0]] 
        during_time = time.perf_counter() - start_time
        tfidf_log('time',during_time)
        to_csv(article,summary_df)
        # find_title_sen(article,summary_df,web_soup)
    except :
        tfidf_log('error','No important word')
        # print('No important word')
        # to_csv(article,summary_df,web_soup)

def NGD(w1,w2,ngd_dict,idf_d = None):
    N = 25270000000.0 # Number of results for "the", proxy for total pages
    N = math.log(N,2) 
    if w1 != w2:
        f_w1 = math.log(number_of_results(w1,ngd_dict),2)
        f_w2 = math.log(number_of_results(w2,ngd_dict),2)
        # f_w2 = math.log(idf_d,2)
        f_w1_w2 = math.log(number_of_results(w1+" "+w2,ngd_dict),2)
        NGD = (max(f_w1,f_w2) - f_w1_w2) / (N - min(f_w1,f_w2))
        return NGD
    else: 
        return 0

def number_of_results(text,ngd_dict):
    ngd = dict_data(text,ngd_dict)
    if ngd == '':
        headers = {'User-Agent': UserAgent().firefox}
        time.sleep(1)
        # text = text.replace(' ','+')
        # url = 'https://www.google.com/search?q='+'益生菌'+'+intext%3A"'+text+'"'
        url = "https://www.google.com/search?q={}".format(text.replace(" ","+"))
        ngd = request_soup(url,'ngd',headers)
        if ngd != None:
            ngd_dict.setdefault(text,ngd)
        else:
            ngd = 1
        time.sleep(1)
    return ngd
    
def count_word(DF):
    try:
        with open('lib/file/TF_益生菌.txt', 'a+',encoding="utf-8") as file:
            file.write(json.dumps(DF,ensure_ascii=False))
    except:
        tfidf_log('error',DF)

def find_title_sen(article,summary_df,web_soup):
    summary_title_df = pd.DataFrame(columns=['word','tf','idf','tfidf','title','sentence'])
    for num in range(len(summary_df)):
        # title = []
        for j in web_soup.find_all(string=re.compile(summary_df['word'].values[num])):
            try:
                h3 = j.find_previous(re.compile('h[1-4]')).get_text().replace('\r','').replace('\n','').replace('\t','').replace('\xa0','')
            except:
                h3 = 'no title'     
            summary_title_df = summary_title_df.append({'word':summary_df['word'].values[num],
                'tf':summary_df['tf'].values[num],
                'idf':summary_df['idf'].values[num],
                'tfidf':summary_df['tfidf'].values[num],
                'title':h3,
                'sentence':j},ignore_index=True)
                # title.append(h3)    
        # summary_df.iloc[num:num+1,5:6] = str(title) 
    to_csv(article,summary_title_df)

def to_csv(article,summary_title_df):
    summary_title_df.insert(0,'article',str(article+1)) 
    file_name = 'lib/file/益生菌.csv'
    if os.path.isfile(file_name):
        summary_title_df.to_csv(file_name,mode='a',header = False,encoding="utf_8_sig",index=0)
    else: 
        summary_title_df.to_csv(file_name,encoding="utf_8_sig",index=0)

def tfidf_log(step,record_object):
    record_time = time.strftime("%Y%m%d %H:%M:%S")
    log_file = open(f'lib/file/{record_time[0:8]}.log',mode='a',encoding='utf-8')
    log_file.write('['+step+'] - {}'.format(record_object)+'\n')

def dict_data(text,dict_data):
    element  = ''
    if text in dict_data:
        element = dict_data[text]
    return element

def update_dict(dict_filename,update_dict):
    with open('lib/json/'+dict_filename+'.json','w',encoding='utf-8') as json_file: 
        json.dump(update_dict,json_file,ensure_ascii=False) 
    tfidf_log('update','update new '+dict_filename+' to json')


user_keyword('益生菌',100)
# final_href_list = ['http://www.kmuh.org.tw/www/kmcj/data/10012/16.htm']
# start_get_html(final_href_list,'益生菌')