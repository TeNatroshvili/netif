from flask import Flask, render_template, request, redirect, send_file, session, flash, url_for, g
import json
from scrapyNetIF.scrapyNetIF.spiders.NetIF import postsomeThing
from report_generation import gen_report
import requests
import subprocess
import os
from datetime import timedelta
from model import User
import time

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)

from mongodb import switches, settings, users
from samba import get_sharedfiles, download, upload
from switch_detection import search_switches

login_manager = LoginManager()

login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"

app = Flask(__name__)
login_manager.init_app(app)
app.secret_key = os.urandom(43)

@login_manager.user_loader
def load_user(user_id):
    user = User.get_by_id(user_id)
    if user is not None:
        return user
    else:
        return None

@app.get("/login")
def login_page():
    return render_template("login.html")

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)
    session.modified = True
    g.user = current_user

@app.route("/dashboard/userdata", methods=["GET"])
@login_required
def userdata():
    user = users.find_one({"_id": session["_user_id"]})
    return {"username":user["username"]}

@app.post("/login")
def login():
    username = request.form["username"]
    password = request.form["password"]
    find_user = users.find_one({"username": username})
    if User.login_valid(username, password):
        loguser = User(find_user["username"], find_user["password"], find_user["_id"])
        login_user(loguser)
        flash('You have been logged in!', 'success')
        next = request.args.get('next')
        return redirect(next or url_for('dashboard'))
    else:
        flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template("login.html")

@app.route("/changePassword", methods=["POST"])
@login_required
def changePassword():
    username = request.form["username"]
    password = request.form["password"]
    newpass = request.form["newpass"]
    print(password +"      " + newpass)
    if User.change_password(username, password, newpass):
        flash("succesfully changed admin password", "success")
        session.clear()
        return redirect(url_for("login"))
    else:
        flash('password change for admin was unsuccessful.', 'danger')
        return redirect(url_for("dashboard"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("succesfully loged out", "success")
    return redirect(url_for("login"))

@app.route("/")
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', switches=switches.find(), reports=get_sharedfiles())

@app.route('/ports')
@login_required
def ports():
    return render_template('ports.html', switches=switches.find())

@app.route('/scrap')
@login_required
def scrap_settings():
    # os.chdir(os.path.dirname(__file__)+"/scrapyNetIF/scrapyNetIF")
    # process = subprocess.Popen(["scrapy", "crawl", "NetIF"])
    # process.wait()
    set = list(settings.find())
    for mydict in set:
        del mydict["_id"]
    return json.dumps(set[0])

@app.route('/ports/scrap')
@login_required
def scrap_port_settings():
    # os.chdir(os.path.dirname(__file__)+"/scrapyNetIF/scrapyNetIF")
    # process = subprocess.Popen(["scrapy", "crawl", "NetIF"])
    # process.wait()
    set = list(settings.find())
    for mydict in set:
        del mydict["_id"]
    return json.dumps(set[0])

@app.route('/load_switches')
@login_required
def load_switches():
    return search_switches()

@app.route('/downloads/<filename>')
@login_required
def download_file(filename):
    return send_file(download(filename), as_attachment=True)

@app.route('/conf/save_user_pass', methods=['POST'])
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
def visualeditor():
    return render_template('visualeditor.html', switches=switches.find())


@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html')


@app.route('/reports/current')
@login_required
def download_last_daily_report():
    # gen_report()
    return send_file("./download/daily_report_21022023.pdf", as_attachment=True)


@app.route('/conf/save_trunk_membership')
@login_required
def save_trunk_membership():
    data = {"_submit": "Apply", "ptc_01": "2", "ptc_02": "2", "ptc_03": "0",
            "ptc_04": "1", "ptc_05": "1", "ptc_06": "0", "ptc_07": "0", "ptc_08": "1"}
    response = requests.post(
        "http://10.128.10.19/trunks/trunks_mem.html", data=data, auth=("username", "Syp2223"))
    return redirect('/')


@app.route('/conf/save_trunk_config')
@login_required
def save_trunk_config():
    data = {"_submit": "Apply", "S01": "3", "F01": "on",
            "S02": "0", "S03": "0", "F01": "", "S04": "0"}
    response = requests.post(
        "http://10.128.10.19/trunks/trunks_config.html", data=data, auth=("username", "Syp2223"))
    return redirect('/')

def clear_download_dict():
    for file in os.listdir('./download'):
        os.remove(os.path.join('./download', file))

if __name__ == '__main__':
    app.run()