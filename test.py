#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from platform import python_version

import urllib.request
import bs4
import re
import subprocess

class color:
    OK = '\33[92m'
    WARN = '\33[93m'
    NG = '\33[91m'
    END_CODE = '\33[0m'

dpath = '~/Downloads/videos/'
axelcmd = 'axel -a -v -n 5 -o '

aname = '';

def downloadMP4fromURL(vurl, fname):
    ffname = vurl.split('/')[-1]
    cmd = axelcmd + dpath + ffname + ' '  + vurl
#    cmd = axelcmd + '"' + dpath + fname + '.mp4" ' + vurl
    print(cmd)
    subprocess.call(cmd, shell=True)

def request_as_fox(url):
	headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0"}
	return urllib.request.Request(url,None,headers)

def getMP4URLfromB9text(src):
    dst = re.sub(r"<.*?>", '', src)
    lines = dst.split("\n")
    hdfound = False
    mp4urls = []
    for line in lines:
        if(hdfound == True):
            print(line)
            mp4urls.append(line)
        if(line.find('HD 720p') >= 0):
            hdfound = True
    return mp4urls
    
    
def getMP4URLfromB9(b9url):
    sp = bs4.BeautifulSoup(urllib.request.urlopen(request_as_fox(b9url)).read(), "lxml")
    infos = sp.find("div", class_="vinfor")
    contributor = infos.find("span", class_="left").a.string
    dls = infos.find("div", id="dl")
    print(color.OK + contributor + color.END_CODE)
    mp4urls = getMP4URLfromB9text(str(dls))
    for mp4url in mp4urls:
        if(mp4url.find('hd3dl') >= 0):
            downloadMP4fromURL(mp4url, aname)

    
def getB9URL(surl):
    sp = bs4.BeautifulSoup(urllib.request.urlopen(surl).read(), "lxml")
    entry = sp.find("div", class_="mainEntrykiji")
    eurls = entry.find_all("a")
    for eurl in eurls:
        siteurl = eurl.get("href")
        sitename = eurl.string
        if(str(sitename) == '【B9】'):
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            print(sitename)
            print(siteurl)
            getMP4URLfromB9(siteurl)

print('Anime Crawleですっ')

rssurl = 'http://tvanimedouga.blog93.fc2.com/?xml'
soup = bs4.BeautifulSoup(urllib.request.urlopen(rssurl).read(), "lxml")

#print(soup.original_encoding)
#print(str(soup))

items =soup.find_all("item")
for itm in items:
    print('+++++++++++++++++++++++++++++++')
    itmurl = itm.get("rdf:about")
    print(str(itmurl))
    aname = itm.description.string
    print(aname)
    anime_title = itm.find("dc:subject").string
    anime_description = itm.find("description").string.replace(anime_title + '　第','')
    anime_epsode = anime_description.split("話")[0]
    src_link = itm.get("rdf:about")

    print(anime_title)
    print(anime_description)
    print(anime_epsode)
    print(src_link)

    #getB9URL(itmurl)


















