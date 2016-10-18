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
    lines = dst.split("\r\n")
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
    mp4urls = [];
    try:
        sp = bs4.BeautifulSoup(urllib.request.urlopen(request_as_fox(b9url)).read(), "lxml")
        infos = sp.find("div", class_="vinfor")
        contributor = infos.find("span", class_="left").a.string
        dls = infos.find("div", id="dl")
        mp4urls = getMP4URLfromB9text(str(dls))
    except:
        print('Failed to get mp4 links...');
    return mp4urls;

# Youtubeアニメ無料動画のアニメ各話エントリページから、B9のURLを見つける
def getB9URL(surl):
    b9urls = []
    try:
        sp = bs4.BeautifulSoup(urllib.request.urlopen(surl).read(), "lxml")
        entry = sp.find("div", class_="mainEntrykiji")
        eurls = entry.find_all("a")
        for eurl in eurls:
            siteurl = eurl.get("href")
            sitename = eurl.string
            if(str(sitename) == '【B9】'):
                b9urls.append(siteurl);
    except:
        print('Failed to get b9 links...');
    return b9urls

# アニメタイトルページからアニメ各話ページヘのURLを得る
def getAnimeURLs(surl):
    anames = [];
    aurls = [];
    if(surl.find('tvanimedouga.blog93.fc2.com') < 0):
        return aurls;
    sp = bs4.BeautifulSoup(urllib.request.urlopen(surl).read(), "lxml")
    entry = sp.find("div", class_="mainEntrykiji")
    aitms = entry.find_all("a")
    for aitm in aitms:
        aurl = aitm.get("href");
        aname = aitm.string;
        if(aname == None):
            continue;
        if(aname.find('話') >= 0):
            anames.append(aname);
            aurls.append(aurl);
    return [anames, aurls];
    


rssurl = 'http://tvanimedouga.blog93.fc2.com/?xml'
soup = bs4.BeautifulSoup(urllib.request.urlopen(rssurl).read(), "lxml")

mainurl = 'http://tvanimedouga.blog93.fc2.com/'
mainsp = bs4.BeautifulSoup(urllib.request.urlopen(mainurl).read(), "lxml");


menu = mainsp.select("#menu1Block")
items = menu[0].find_all("li");

for itm in items:
    atitle = itm.a.string;
    aurl = itm.a.get("href");
    print("---------------------")
    print(itm.a.string);
    print(aurl);
    [snames, surls] = getAnimeURLs(aurl);
    for (surl, sname) in zip(surls, snames):
        b9urls = getB9URL(surl);
        print(sname);
        print(surl);
        for b9url in b9urls:
            mp4urls = getMP4URLfromB9(b9url);
            if(len(mp4urls) != 0):
                print('+++++' + b9url + '+++++');
                print(mp4urls);















