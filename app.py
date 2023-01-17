from flask import Flask, render_template, request, redirect
import json
import scrapy
from scrapyNetIF.scrapyNetIF.spiders.NetIF import postsomeThing
import requests
app = Flask(__name__)



@app.route('/save_system_snmp',methods=['POST'])
def save_system_snmp():
    snmp = request.form["snmp_on"]
    data = {"_submit": "Apply", "btnSaveSettings": "APPLY"}
    #check with data need to be saved when checkboxes or set text automatically
    if('1'==snmp):
        data["SNMP"] = "1"

    response = requests.post("http://10.128.10.19/system/system_snmp.html", data=data, auth=("username", "Syp2223"))
    return redirect('/')
    

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/visualeditor')
def visualeditor():
    return render_template('visualeditor.html')

if __name__ == '__main__':
    app.run(debug=1)
