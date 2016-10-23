#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from platform import python_version

import urllib.request
import bs4
import re
import subprocess
import psycopg2
import psycopg2.extras
from datetime import datetime as dt


dpath = '~/Downloads/videos/'
axelcmd = 'axel -a -v -n 5 -o '

aname = ''

dbhost = '133.130.106.168'
dbname = 'anime'
dbuser = 'ery'
dbpswd = 'biztablet'

class color:
    OK = '\33[92m'
    WARN = '\33[93m'
    NG = '\33[91m'
    END_CODE = '\33[0m'

def request_as_fox(url):
    headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0"}
    return urllib.request.Request(url,None,headers)

# ダウンロードを実行
def downloadMP4fromURL(vurl):
    fname = vurl.split('/')[-1]
    cmd = axelcmd + dpath + fname + ' '  + vurl
    subprocess.call(cmd, shell=True)
    return fname
    
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
    mp4urls = []
    try:
        sp = bs4.BeautifulSoup(urllib.request.urlopen(request_as_fox(b9url)).read(), "lxml")
        infos = sp.find("div", class_="vinfor")
        contributor = infos.find("span", class_="left").a.string
        dls = infos.find("div", id="dl")
        mp4urls = getMP4URLfromB9text(str(dls))
    except:
        print('Failed to get mp4 links...')
    return mp4urls

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
                b9urls.append(siteurl)
    except:
        print('Failed to get b9 links...')
    return b9urls

# アニメタイトルページからアニメ各話ページヘのURLを得る
def getAnimeURLs(surl):
    anames = []
    aurls = []
    if(surl.find('tvanimedouga.blog93.fc2.com') < 0):
        return aurls
    sp = bs4.BeautifulSoup(urllib.request.urlopen(surl).read(), "lxml")
    entry = sp.find("div", class_="mainEntrykiji")
    aitms = entry.find_all("a")
    for aitm in aitms:
        aurl = aitm.get("href")
        aname = aitm.string
        if(aname == None):
            continue
        if(aname.find('話') >= 0):
            anames.append(aname)
            aurls.append(aurl)
    return [anames, aurls]

# SQLデータベースに対してアニメ各話情報をもとに登録、更新する
# まず、src_linkを元に、登録済みであるか判別する
# 登録済みであれば、UPDATE
# でなければINSERTする
def registerAnime(anime_infos, dbcur):
    """
    print(anime_name);
    print(anime_discription);
    print(episode);
    print(src_link);
    print(mp4links);
    print(dt.now().strftime('%Y-%m-%d %H:%M:%S'))
    :param anime_infos:
    :param dbcur:
    :return:
    """
    anime_name = anime_infos[0];
    anime_discription = anime_infos[1];
    anime_episode = anime_infos[2];
    src_link = anime_infos[3];
    mp4_links = anime_infos[4];
    date_time = anime_infos[5];

    #登録済みか検索
    is_registered = False;
    dbcur.execute("select id from anime where src_link = (%s)", [src_link]);
    rslt = [];
    for row in dbcur:
        rslt.append(row)

    if(len(rslt) != 0):
        is_registered = True;

    if(is_registered == True):
        #登録済みである場合

        #dbcur.execute("")
        dbcur.execute("UPDATE anime set (anime_name, anime_description, date, episode, src_link) = ((%s), (%s), (%s), (%s), (%s)) where src_link = (%s)", [anime_name, anime_discription, date_time, anime_episode, src_link, src_link]);


    else:
        #登録済みでない場合
        dbcur.execute("INSERT INTO anime(anime_name, anime_description, date, episode, src_link) VALUES((%s), (%s), (%s), (%s), (%s))", [anime_name, anime_discription, date_time, anime_episode, src_link]);

    #MP4 linkの登録
    linkidx = 1;
    mp4linkstr = '';
    for mp4link in mp4links:
        mp4linkstr += mp4link + "|";
        if(linkidx <= 3):
            dbcur.execute("update anime set link%s = (%s) where src_link = (%s)", [(linkidx), mp4link, src_link]);
        linkidx += 1;
    dbcur.execute("update anime set links = (%s) where src_link = (%s)", [mp4linkstr, src_link]);

    
#MAIN

"""
必要な情報

* anime_name : アニメ題名
* anime_discription : アニメの各話における題名など
* episode : アニメの話数
* date : 登録日（データベース登録日）
* links : MP4リンク
* filepath : ダウンロードしたファイルへのパス

ながれ
１．各情報をスクレイピングでゲットする
２．同じアニメが登録されているか調べる（アニメの題名と話数で判別?　もしかしたらアニメ各話のブログURLで判別するほうがいいかもしれない）
３．足りない情報がゲットできていればそれを登録する(情報の更新)

"""

# Create connection to anime DB
dbcn = psycopg2.connect("host=" + dbhost + " dbname=" + dbname + " user=" + dbuser + " password=" + dbpswd)
dbcn.autocommit = True
cur = dbcn.cursor()
print(cur)

#DB tests
cur.execute("select version()")
for row in cur:
    print(row)


dcur = dbcn.cursor(cursor_factory=psycopg2.extras.DictCursor)
dcur.execute("select id, anime_name from anime")
for row in dcur:
    print(row["id"], row["anime_name"])


rssurl = 'http://tvanimedouga.blog93.fc2.com/?xml'
soup = bs4.BeautifulSoup(urllib.request.urlopen(rssurl).read(), "lxml")

mainurl = 'http://tvanimedouga.blog93.fc2.com/'
mainsp = bs4.BeautifulSoup(urllib.request.urlopen(mainurl).read(), "lxml")




menu = mainsp.select("#menu1Block")
items = menu[0].find_all("li");

for itm in items:
    #アニメROOTループ
    anime_name = itm.a.string;
    anime_main_link = itm.a.get("href");
    print("---------------------")
    print(itm.a.string);
    print(anime_main_link);

    [anime_discriptions, src_links] = getAnimeURLs(anime_main_link);

    for (src_link, anime_discription) in zip(src_links, anime_discriptions):
        #アニメ各話ループ このループが基本になる

        b9urls = getB9URL(src_link);
        mp4links = [];
        episode = str(anime_discription).split("話")[0];

        # 登録済みか検索
        is_registered = False;
        cur.execute("select id from anime where src_link = (%s)", [src_link]);
        rslt = [];
        for row in cur:
            rslt.append(row)
        if (len(rslt) != 0):
            print("Already Registered!!!")
            continue;

        for b9url in b9urls:

            #B9リンクループ
            mp4urls = getMP4URLfromB9(b9url);
            if(len(mp4urls) != 0):
                for mp4url in mp4urls:
                    mp4links.append(mp4url);

        print('##############################');
        print(anime_name);
        print(anime_discription);
        print(episode);
        print(src_link);
        print(mp4links);
        print(dt.now().strftime('%Y-%m-%d %H:%M:%S'))
        registerAnime([anime_name, anime_discription, episode, src_link, mp4links, dt.now().strftime('%Y-%m-%d %H:%M:%S')], cur);


