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
from flask import Flask, render_template
import json



#DB設定
dbhost = '133.130.106.168'
dbname = 'anime'
dbuser = 'ery'
dbpswd = 'biztablet'


#DBのアニメ題名すべてを返す
def get_all_anime_names():
    # Create connection to anime DB
    dbcn = psycopg2.connect("host=" + dbhost + " dbname=" + dbname + " user=" + dbuser + " password=" + dbpswd)
    cur = dbcn.cursor()

    cur.execute("SELECT DISTINCT anime_name FROM anime")
    anime_names = []
    for row in cur:
        anime_names.append(str(row[0]));

    #切断
    cur.close()
    dbcn.close()

    return anime_names;


#ある題名のアニメのすべての話を返す
def get_all_episodes(anime_name):
    # Create connection to anime DB
    dbcn = psycopg2.connect("host=" + dbhost + " dbname=" + dbname + " user=" + dbuser + " password=" + dbpswd)
    cur = dbcn.cursor()

    cur.execute("SELECT anime_description FROM anime WHERE anime_name = (%s)", [str(anime_name)])
    anime_ds = []
    for row in cur:
        anime_ds.append(str(row[0]));
    # 切断
    cur.close()
    dbcn.close()
    return anime_ds

#ある題名のアニメのすべての話を返す + 詳細な情報
def get_all_info_by_anime_name(anime_name):
    # Create connection to anime DB
    dbcn = psycopg2.connect("host=" + dbhost + " dbname=" + dbname + " user=" + dbuser + " password=" + dbpswd)
    cur = dbcn.cursor()

    cur.execute("SELECT anime_description, episode, src_link, links FROM anime WHERE anime_name = (%s)", [str(anime_name)])
    anime_infos = []
    for row in cur:
        links = str(row[3]).split('|')
        links.pop()
        anime_infos.append([str(row[0]), str(row[1]), str(row[2]), links])
    # 切断
    cur.close()
    dbcn.close()
    return anime_infos


app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html', message="Hello")


@app.route("/t_test")
def t_test():
    return render_template('index.html', message="test")


@app.route("/anime/<a_name>")
def hndl_anime_name(a_name):
    anime_infos = sorted(get_all_info_by_anime_name(a_name), key=lambda x: float(x[1]))
    return render_template('anime_infos.html', message=anime_infos)


@app.route("/all")
def show_all_animes():
    all_animes = get_all_anime_names()
    all_anime_links = []
    for anime_name in all_animes:
        link = "/anime/" + anime_name
        all_anime_links.append([anime_name, link])
    return render_template('all_animes.html', message=all_anime_links)

@app.route("/arraytest/<a_name>")
def hndl_array(a_name):
    data = [str(a_name), str(a_name), str(a_name)]
    return render_template('arraytest.html', message=data)

@app.route("/video")
def video_test():
    return render_template('videotest.html', message="うんこ")


if __name__ == "__main__":
    app.run(debug=True)


















