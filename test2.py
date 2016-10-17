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


def request_as_fox(url):
	headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0"}
	return urllib.request.Request(url,None,headers)

# ダウンロードを実行
def downloadMP4fromURL(vurl):
    fname = vurl.split('/')[-1]
    cmd = axelcmd + dpath + fname + ' '  + vurl
    subprocess.call(cmd, shell=True)
    return fname;
    
# B9のエントリテキストからHD画質のMP4リンクを見つける
def getMP4URLfromB9text(src):
    dst = re.sub(r"<.*?>", '', src)
    lines = dst.split("\n")
    hdfound = False
    mp4urls = []
    for line in lines:
        if(hdfound == True):
            mp4urls.append(line)
        if(line.find('HD 720p') >= 0):
            hdfound = True
    return mp4urls
    
# B9のページからHD画質のMP4に繋がるリンクを探す
def getMP4URLfromB9(b9url):
    sp = bs4.BeautifulSoup(urllib.request.urlopen(request_as_fox(b9url)).read(), "lxml")
    infos = sp.find("div", class_="vinfor")
    contributor = infos.find("span", class_="left").a.string
    dls = infos.find("div", id="dl")
    mp4urls = getMP4URLfromB9text(str(dls))
    return mp4urls;

# Youtubeアニメ無料動画のアニメ各話エントリページから、B9のURLを見つける
def getB9URL(surl):
    b9urls = []
    sp = bs4.BeautifulSoup(urllib.request.urlopen(surl).read(), "lxml")
    entry = sp.find("div", class_="mainEntrykiji")
    eurls = entry.find_all("a")
    for eurl in eurls:
        siteurl = eurl.get("href")
        sitename = eurl.string
        if(str(sitename) == '【B9】'):
            b9urls.append(siteurl);
    return b9urls



rssurl = 'http://tvanimedouga.blog93.fc2.com/?xml'
soup = bs4.BeautifulSoup(urllib.request.urlopen(rssurl).read(), "lxml")

items =soup.find_all("item")
for itm in items:
    itmurl = itm.get("rdf:about");
    atitle = itm.title.string;
    aname = itm.description.string;
    b9urls = getB9URL(itmurl);
    print(atitle + ' +++++++++++++++++++++++');
    print('B9URLs')
    print(b9urls)
    for b9url in b9urls:
        mp4urls = getMP4URLfromB9(b9url);
        print('MP4URLs')
        print(mp4urls)
    


















