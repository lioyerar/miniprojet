#!/usr/bin/env python3
#coding ut-8

import bottle
import requests
import json
from bs4 import BeautifulSoup


global adresses, jsons
adresses = []
jsons = []

def searchCache(name):
    cache = -1
    for i in range(len(adresses)):
        if (adresses[i] == 'https://dblp.org/search/publ/api?q='+name+'&format=json&h=1000'):
            cache = i
            break
    if cache == -1 :
        print("Cache Miss")
        adresses.append('https://dblp.org/search/publ/api?q='+name+'&format=json&h=1000')
        r = requests.get('https://dblp.org/search/publ/api?q='+name+'&format=json&h=1000')
        data = json.loads(r.content)
        jsons.append(data)
    else:
        print("Cache Hit")
        data = jsons[cache]
    return data

def co_author(hits,boolean):
    co_authors = []
    for hit in hits:
        if(hit['info']['type'] == "Conference and Workshop Papers" or  hit['info']['type'] == "Journal Articles"):
            if (type(hit['info']['authors']['author']) is list):
                for author in hit['info']['authors']['author']:
                    if author not in co_authors:
                        co_authors.append(author)
    if(boolean == True):
        return len(co_authors)
    else:
        string = ''
        for temp in co_authors:
            string += temp+'<br>'
        return string

@bottle.route("/authors/<name>")
@bottle.view('index.tpl')
def page(name):
    data = searchCache(name)
    nb_co = co_author(data['result']['hits']['hit'],True)
    return {'body':'Nombre de publication:'+data['result']['hits']['@total']+'<br> Les co-auteurs: '+str(nb_co)
            }


@bottle.route('/<name>/publications')
@bottle.view('index.tpl')
def search(name):
    data = searchCache(name)
    hits = data['result']['hits']['hit']
    temp =[]
    for hit in hits:
        if(hit['info']['type'] == "Conference and Workshop Papers" or  hit['info']['type'] == "Journal Articles"):
            temp.append(hit['info']['title'])
    pubs=''
    for pub in temp:
        pubs += pub+'<br>'


    return {'body': pubs }

@bottle.route('/authors/<name>/coauthors')
@bottle.view('index.tpl')
def coauthor(name):
    data = searchCache(name)
    nb_co = co_author(data['result']['hits']['hit'],False)
    return {'body':nb_co}


@bottle.route('/authors/<name>/synthesis')
@bottle.view("index.tpl")
def syn(name):
    data = searchCache(name)
    hits = data['result']['hits']['hit']
    for hit in hits:
        print(hit)
        search_key = hit['info']['venue']
        search_key = search_key.replace(' ','+')
        search_key = search_key.replace('.','')
        if(hit['info']['type'] == "Conference and Workshop Papers"):
            r = requests.get('http://portal.core.edu.au/conf-ranks/?search='+search_key+'&by=all&source=all&sort=atitle&page=1')
            soup = BeautifulSoup(r.content,'html.parser')
            tbody = soup.find_all('tbody')
            print(tbody)
        elif( hit['info']['type'] == "Journal Articles"):
            r = requests.get('http://portal.core.edu.au/jnl-ranks/?search='+search_key+'&by=all&source=ERA2010%0D%0A&sort=atitle&page=1')
            soup = BeautifulSoup(r.content,'html.parser')
            tbody = soup.find_all('tbody')
            print(tbody)
    return {'body':pub}



bottle.run(bottle.app(), host='127.0.0.1', port=8080, debug= True, reloader=True)
