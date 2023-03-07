from flask import Flask, render_template, request, redirect, send_file
import json
from scrapyNetIF.scrapyNetIF.spiders.NetIF import postsomeThing
from report_generation import gen_report
import requests
import subprocess
import os

from mongodb import switches, settings
from samba import get_sharedfiles, download, upload
from switch_detection import search_switches

app = Flask(__name__)


@app.route('/')
def dashboard():
    return render_template('dashboard.html', switches=switches.find(), reports=get_sharedfiles())


@app.route('/ports')
def ports():
    return render_template('ports.html', switches=switches.find())


@app.route('/scrap')
def scrap_settings():
    # os.chdir(os.path.dirname(__file__)+"/scrapyNetIF/scrapyNetIF")
    # process = subprocess.Popen(["scrapy", "crawl", "NetIF"])
    # process.wait()
    set = list(settings.find())
    for mydict in set:
        del mydict["_id"]
    return json.dumps(set[0])


@app.route('/ports/scrap')
def scrap_port_settings():
    # os.chdir(os.path.dirname(__file__)+"/scrapyNetIF/scrapyNetIF")
    # process = subprocess.Popen(["scrapy", "crawl", "NetIF"])
    # process.wait()
    set = list(settings.find())
    for mydict in set:
        del mydict["_id"]
    return json.dumps(set[0])


@app.route('/load_switches')
def load_switches():
    return search_switches()


@app.route('/downloads/<filename>')
def download_file(filename):
    return send_file(download(filename), as_attachment=True)


@app.route('/conf/save_user_pass', methods=['POST'])
def save_user_pass():
    username = request.form["username"]
    cur_pass = request.form["current_password"]
    new_pass = request.form["new_password"]
    confirm_pass = request.form["confirm_password"]

    session = requests.Session()
    session.post('http://10.137.4.41/htdocs/login/login.lua',
                 data={"username": "admin", "password": "Syp2023hurra"})

    data = {"user_name": username,
            "current_password": cur_pass,
            "new_password": new_pass,
            "confirm_new_passwd": confirm_pass,
            "b_form1_submit": "Apply",
            "b_form1_clicked": "b_form1_submit"}

    response = session.post("http://10.137.4.41/htdocs/pages/base/user_accounts.lsp",
                             data=data, cookies=session.cookies.get_dict())
    
    session.close()
    return redirect('/')


@app.route('/conf/save_system_settings', methods=['POST'])
def save_system_settings():
    ipaddress = request.form["ipadress"]
    subnetmask = request.form["subnetmask"]
    gatewayaddress = request.form["gatewayadress"]
    name = request.form["systemname"]
    snmp = request.form["snmp"]
    
    session = requests.Session()
    session.post('http://10.137.4.41/htdocs/login/login.lua',
                 data={"username": "admin", "password": "Syp2023hurra"})

    data = {"sys_name": "SW-N313",
            "sys_location": "N313",
            "sys_contact": "",
            "b_form1_submit": "Apply",
            "b_form1_clicked": "b_form1_submit"}

    response = session.post("http://10.137.4.41/htdocs/pages/base/dashboard.lsp",
                             data=data, cookies=session.cookies.get_dict())

    data = {"protocol_type_sel[]": "static",
            "ip_addr": "10.137.4.41",
            "subnet_mask": "255.255.0.0",
            "gateway_address": "10.137.255.254",
            "session_timeout": "5",
            "mgmt_vlan_id_sel[]": "1",
            "mgmt_port_sel[]": "none",
            "snmp_sel[]": "enabled",
            "community_name": "public",
            "b_form1_submit": "Apply",
            "b_form1_clicked": "b_form1_submit"}

    response = session.post("http://10.137.4.41/htdocs/pages/base/network_ipv4_cfg.lsp",
                             data=data, cookies=session.cookies.get_dict())
    
    session.close()
    return redirect('/')

@app.route('/conf/save_port_configuration', methods=['POST'])
def save_port_configuration():
    session = requests.Session()
    response = session.post('http://10.137.4.41/htdocs/login/login.lua', data={"username":"admin","password":"Syp2023hurra"})

    #admin_mode_sel%5B%5D=enabled&phys_mode_sel%5B%5D=4&port_descr=&intf=4&b_modal1_clicked=b_modal1_submit
    admin_mode = request.form["admin_mode_sel[]"]
    phys_mode = request.form["phys_mode_sel[]"]
    port_descr = request.form["port_descr"]
    intf = request.form["intf"]

    data = {"admin_mode_sel[]": admin_mode,
            "phys_mode_sel[]": phys_mode,
            "port_descr": port_descr,
            "intf": intf,
            "b_modal1_clicked": "b_modal1_submit"}
    
    response = session.post("http://10.137.4.41/htdocs/pages/base/port_summary_modal.lsp", data=data, cookies=session.cookies.get_dict())
    session.post("http://10.137.4.41/htdocs/lua/ajax/save_cfg.lua?save=1", cookies=session.cookies.get_dict())
    session.get("http://10.137.4.41/htdocs/pages/main/logout.lsp", cookies=session.cookies.get_dict())
    
    return redirect('/ports')

@app.route('/conf/save_all_port_configuration', methods=['POST'])
def save_all_port_configuration():
    session = requests.Session()
    response = session.post('http://10.137.4.41/htdocs/login/login.lua', data={"username":"admin","password":"Syp2023hurra"})

    #phys_mode_sel%5B%5D=1&port_descr=&intf=all&b_modal1_clicked=b_modal1_submit
    phys_mode = request.form["phys_mode_sel[]"]
    port_descr = request.form["port_descr"]

    data = {"phys_mode_sel[]": phys_mode,
            "port_descr": port_descr,
            "intf": "all",
            "b_modal1_clicked": "b_modal1_submit"}
    
    response = session.post("http://10.137.4.41/htdocs/pages/base/port_summary_modal.lsp", data=data, cookies=session.cookies.get_dict())
    session.post("http://10.137.4.41/htdocs/lua/ajax/save_cfg.lua?save=1", cookies=session.cookies.get_dict())
    session.get("http://10.137.4.41/htdocs/pages/main/logout.lsp", cookies=session.cookies.get_dict())
    
    return redirect('/ports')


@app.route('/visualeditor')
def visualeditor():
    return render_template('visualeditor.html', switches=switches.find())


@app.route('/reports')
def reports():
    return render_template('reports.html')


@app.route('/reports/current')
def download_last_daily_report():
    # gen_report()
    return send_file("./download/daily_report_21022023.pdf", as_attachment=True)


@app.route('/conf/save_trunk_membership')
def save_trunk_membership():
    data = {"_submit": "Apply", "ptc_01": "2", "ptc_02": "2", "ptc_03": "0",
            "ptc_04": "1", "ptc_05": "1", "ptc_06": "0", "ptc_07": "0", "ptc_08": "1"}
    response = requests.post(
        "http://10.128.10.19/trunks/trunks_mem.html", data=data, auth=("username", "Syp2223"))
    return redirect('/')


@app.route('/conf/save_trunk_config')
def save_trunk_config():
    data = {"_submit": "Apply", "S01": "3", "F01": "on",
            "S02": "0", "S03": "0", "F01": "", "S04": "0"}
    response = requests.post(
        "http://10.128.10.19/trunks/trunks_config.html", data=data, auth=("username", "Syp2223"))
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=1)

def clear_download_dict():
    for file in os.listdir('./download'):
        os.remove(os.path.join('./download', file))