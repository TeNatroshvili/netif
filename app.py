from flask import Flask, render_template, request, redirect, send_file
import json
from scrapyNetIF.scrapyNetIF.spiders.NetIF import postsomeThing
from report_generation import gen_report
import requests
import subprocess 
import os

from mongodb import switches, settings
from samba import get_sharedfiles

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html', switches = switches.find(), reports = get_sharedfiles())


@app.route('/conf/save_system_snmp',methods=['POST'])
def save_system_snmp():
    snmp = request.form["snmp_on"]
    data = {"_submit": "Apply", "btnSaveSettings": "APPLY"}
    #check with data need to be saved when checkboxes or set text automatically
    if('1'==snmp):
        data["SNMP"] = "1"

    response = requests.post("http://10.128.10.19/system/system_snmp.html", data=data, auth=("username", "Syp2223"))
    return redirect('/')
    

@app.route('/conf/save_name',methods=['POST'])
def save_name():
    data = {"_submit": "Apply", "nm": "name1", "location":"", "contact":"", "btnSaveSettings":"APPLY"}
    #check with data need to be saved when checkboxes or set text automatically

    response = requests.post("http://10.128.10.19/system/system_snmp.html", data=data, auth=("username", "Syp2223"))
    return redirect('/')

@app.route('/scrap')
def scrap_settings():
    os.chdir(os.path.dirname(__file__)+"/scrapyNetIF/scrapyNetIF")
    process = subprocess.Popen(["scrapy", "crawl", "NetIF"])
    process.wait()
    set = list(settings.find())
    for mydict in set:
        del mydict["_id"]
    return json.dumps(set[0])


@app.route('/conf/save_system_settings',methods=['POST'])
def save_system_settings():
    print(request)
    ipaddress = request.form["ipadress"]
    subnetmask = request.form["subnetmask"]
    gatewayaddress = request.form["gatewayadress"]
    name = request.form["systemname"]

    data = {"_submit": "Apply"}

    data["nm"] = name

    data["btnSaveSettings"] = "APPLY"
    print(data)

    response = requests.post("http://10.128.10.19/system/system_name.html", data=data, auth=("username", "Syp2223"))

    data = {"_submit": "Apply"}

    #data["ip"] = ipaddress
    data["sm"] = subnetmask
    data["gw"] = gatewayaddress

    data["btnSaveSettings"] = "APPLY"

    # response = requests.post("http://10.128.10.19/system/system_ls.html", data=data, auth=("username", "Syp2223"))

    return redirect('/')

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

@app.route('/conf/save_trunk_membership')
def save_trunk_membership():
    data = {"_submit": "Apply", "ptc_01": "2", "ptc_02": "2","ptc_03": "0","ptc_04": "1","ptc_05": "1","ptc_06": "0","ptc_07": "0","ptc_08": "1"}
    response = requests.post("http://10.128.10.19/trunks/trunks_mem.html", data=data, auth=("username", "Syp2223"))
    return redirect('/')

@app.route('/conf/save_trunk_config')
def save_trunk_config():
    data = {"_submit": "Apply", "S01": "3","F01":"on","S02":"0","S03":"0","F01":"","S04":"0"}
    response = requests.post("http://10.128.10.19/trunks/trunks_config.html", data=data, auth=("username", "Syp2223"))
    return redirect('/')

# @app.route('/conf/save_lacp')
# def save_lacp():
#     data = {"_submit": "Apply","M01":"ON", "K01": "33","M02":"ON", "K02": "133", "K03": "0", "M06":"ON","K06": "0","K07": "","K08": "0"}
#     response = requests.post("http://10.128.10.19/trunks/lacp.html", data=data, auth=("username", "Syp2223"))
#     return redirect('/')

if __name__ == '__main__':
    app.run(debug=1)