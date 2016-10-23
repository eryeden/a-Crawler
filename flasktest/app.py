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

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello"


if __name__ == "__main__":
    app.run(debug=True)
