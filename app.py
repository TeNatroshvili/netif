from flask import Flask, render_template, request, redirect, send_file
from bson.json_util import dumps
from scrapyNetIF.scrapyNetIF.spiders.NetIF import postsomeThing
from report_generation import gen_report
import requests

from mongodb import switches, settings
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
    print(settings)
    return render_template('dashboard.html', switches = switches.find(), settings = settings.find()) #dumps wenn gefixt

@app.route('/visualeditor')
def visualeditor():
    return render_template('visualeditor.html', switches = switches.find())

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/reports/current')
def download_last_daily_report():
    gen_report()
    return send_file("./reports/daily_report.pdf", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=1)