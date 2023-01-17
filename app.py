from flask import Flask, render_template, request
import json
import scrapy
from scrapyNetIF.scrapyNetIF.spiders.NetIF import postsomeThing
from flask import request,redirect
import requests

from mongodb import switches
app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/visualeditor')
def visualeditor():
    return render_template('visualeditor.html', switches = switches.find())

if __name__ == '__main__':
    app.run(debug=1)