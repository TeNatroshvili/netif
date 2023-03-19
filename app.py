from flask import (
    Flask, 
    render_template, 
    redirect, 
    send_file, 
    flash, 
    url_for,
    request, 
    g,
    session
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from datetime import timedelta
import json
import os
import requests
import threading

# custom imports
from mongodb import (
    switches, 
    settings, 
    users
)
from samba import (
    get_sharedfiles, 
    download, 
    upload
)
from switch_detection import search_switches
from model import User
from login_credentials import switch_login_credentials
from scraping_1810 import scrap_switch_1810
from scraping_1820 import scrap_switch_1820

import requests


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


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("succesfully loged out", "success")
    return redirect(url_for("login"))


@app.route("/changePassword", methods=["POST"])
@login_required
def changePassword():
    username = request.form["username"]
    password = request.form["password"]
    newpass = request.form["newpass"]
    if User.change_password(username, password, newpass):
        flash("succesfully changed admin password", "success")
        session.clear()
        return redirect(url_for("login"))
    else:
        flash('password change for admin was unsuccessful.', 'danger')
        return redirect(url_for("dashboard"))


# dashboard

@app.route("/")
@login_required
def default():
    return redirect(url_for("dashboard"))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', switches=switches.find(), reports=get_sharedfiles())


@app.route("/dashboard/userdata", methods=["GET"])
@login_required
def userdata():
    user = users.find_one({"_id": session["_user_id"]})
    return {"username":user["username"]}


@app.route('/dashboard/scrap/<ip>')
@login_required
def scrap_settings(ip):
    model = get_model_from_ip(ip)
    if("1810" in model):
        scrap_switch_1810(ip)
    elif("1820" in model):
        scrap_switch_1820(ip)
    else:
        print("Switch Model not supported")
        return 'not supported', 501

    setting = settings.find_one({"ip_address":ip})
    print(setting)
    print("ip"+ip)
    del setting["_id"]
    return json.dumps(setting)


@app.route('/dashboard/load_switches')
@login_required
def load_switches():
    return search_switches()


# ports

@app.route('/ports')
@login_required
def ports():
    return render_template('ports.html', switches=switches.find())


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

# download

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    return send_file(download(filename), as_attachment=True)


# configuration

@app.route('/conf/save_system_settings/<ip>', methods=['POST'])
@login_required
def save_system_settings(ip):
    ipaddress = request.form["ipaddress"]
    subnetmask = request.form["subnetmask"]
    gatewayaddress = request.form["gatewayaddress"]
    name = request.form["systemname"]
    snmp = request.form["snmp"]
    
    model = get_model_from_ip(ip)
    if("1810" in model):
        session = requests.Session()
    elif("1820" in model):
        
        
        session = requests.Session()
        session.post('http://10.137.4.41/htdocs/login/login.lua',
                    data=switch_login_credentials)

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
    else:
        print("Switch Model not supported")
    
    session.close()
    return redirect('/')


@app.route('/conf/save_port_configuration/<ipaddress>', methods=['POST'])
@login_required
def save_port_configuration(ipaddress):
    model = get_model_from_ip(ipaddress)
    if("1820" in model):
        session = requests.Session()
        response = session.post('http://'+ipaddress+'/htdocs/login/login.lua', data=switch_login_credentials)

        #admin_mode_sel%5B%5D=enabled&phys_mode_sel%5B%5D=4&port_descr=&intf=4&b_modal1_clicked=b_modal1_submit
        admin_mode = request.form["admin_mode"]
        phys_mode = request.form["phys_mode"]
        port_descr = request.form["port_descr"]
        intf = request.form["intf"]
              
        data = {"admin_mode_sel[]": admin_mode,
                "phys_mode_sel[]": phys_mode,
                "port_descr": port_descr,
                "intf": intf,
                "b_modal1_clicked": "b_modal1_submit"}
    
        response = session.post("http://"+ipaddress+"/htdocs/pages/base/port_summary_modal.lsp", data=data, cookies=session.cookies.get_dict())
        session.post("http://"+ipaddress+"/htdocs/lua/ajax/save_cfg.lua?save=1", cookies=session.cookies.get_dict())
        session.get("http://"+ipaddress+"/htdocs/pages/main/logout.lsp", cookies=session.cookies.get_dict())
    
    elif("1810" in model):
        session = requests.Session()
        response = session.post('http://'+ipaddress+'/config/login', data=switch_login_credentials["password"])
        seid_cookie = session.cookies.get_dict()

        seid_cookie_str = '; '.join([f'{key}={value}' for key, value in seid_cookie.items()])
        cookies = {'seid': seid_cookie_str, 'deviceid': 'YWRtaW46U3lwMjAyM2h1cnJh'}

        # port=1&admin=on&speed=1A0A0&sid=-1
        speed_id = request.form["phys_mode"]
        port = request.form["intf"]

        match speed_id:
            case '1':
                speed = "1A0A0"
            case '4':
                speed = "0A1A0"
            case '5':
                speed = "0A1A1"
            case '2':
                speed = "0A2A0"
            case '3':
                speed = "0A2A1"

        if request.form["admin_mode"] == "enabled":
            admin = "on"
            data = {"port": port,
                    "admin": admin,
                    "speed": speed,
                    "sid": "-1"}
            response=session.post('http://'+ipaddress+'/update/config/ports', data=data, cookies=cookies)
        else:
            data = {"port": port,
                    "speed": speed,
                    "sid": "-1"}
            response=session.post('http://'+ipaddress+'/update/config/ports', data=data, cookies=cookies)

        session.post("http://"+ipaddress+"/config/logout", cookies=cookies)
    
    return redirect('/ports')


@app.route('/conf/save_all_port_configuration/<ipaddress>', methods=['POST'])
@login_required
def save_all_port_configuration(ipaddress):
    session = requests.Session()
    response = session.post('http://'+ipaddress+'/htdocs/login/login.lua', data=switch_login_credentials)

    #phys_mode_sel%5B%5D=1&port_descr=&intf=all&b_modal1_clicked=b_modal1_submit
    phys_mode = request.form["phys_mode"]
    port_descr = request.form["port_descr"]

    data = {"phys_mode_sel[]": phys_mode,
            "port_descr": port_descr,
            "intf": "all",
            "b_modal1_clicked": "b_modal1_submit"}
    
    response = session.post("http://"+ipaddress+"/htdocs/pages/base/port_summary_modal.lsp", data=data, cookies=session.cookies.get_dict())
    session.post("http://"+ipaddress+"/htdocs/lua/ajax/save_cfg.lua?save=1", cookies=session.cookies.get_dict())
    session.get("http://"+ipaddress+"/htdocs/pages/main/logout.lsp", cookies=session.cookies.get_dict())
    
    return redirect('/ports')


@app.route('/conf/save_port_mirroring/<ipaddress>', methods=['POST'])
@login_required
def save_port_mirroring(ipaddress):
    model = get_model_from_ip(ipaddress)
    if("1820" in model):
        session = requests.Session()
        response = session.post('http://'+ipaddress+'/htdocs/login/login.lua', data=switch_login_credentials)

        #port_mirroring_sel%5B%5D=enabled&destination_port_sel%5B%5D=1&sorttable1_length=-1&b_form1_submit=Apply&b_form1_clicked=b_form1_submit
        port_mirroring = request.form["port_mirroring"]
        destination_port = request.form["destination_port"]

        data = {"port_mirroring_sel[]": port_mirroring,
                "destination_port_sel[]": destination_port,
                "sorttable1_length": "-1",
                "b_form1_submit": "Apply",
                "b_form1_clicked": "b_form1_submit"}
        
        response = session.post("http://"+ipaddress+"/htdocs/pages/base/port_mirror.lsp", data=data, cookies=session.cookies.get_dict())
        session.post("http://"+ipaddress+"/htdocs/lua/ajax/save_cfg.lua?save=1", cookies=session.cookies.get_dict())
        session.get("http://"+ipaddress+"/htdocs/pages/main/logout.lsp", cookies=session.cookies.get_dict())
    elif("1810" in model):
        session = requests.Session()
        response = session.post('http://'+ipaddress+'/config/login', data=switch_login_credentials["password"])
        seid_cookie = session.cookies.get_dict()

        seid_cookie_str = '; '.join([f'{key}={value}' for key, value in seid_cookie.items()])
        cookies = {'seid': seid_cookie_str, 'deviceid': 'YWRtaW46U3lwMjAyM2h1cnJh'}
        
        # portselect=1&mode_1=4&mode_2=4&mode_3=4&mode_4=4&mode_5=4&mode_6=4
        # &mode_7=4&mode_8=4&mode_9=4&mode_10=4&mode_11=4&mode_12=4&mode_13=4
        # &dummy=undefined&mode_14=4&mode_15=4&mode_16=4&mode_17=4&mode_18=4
        # &mode_19=4&mode_20=4&mode_21=4&mode_22=4&mode_23=4&mode_24=4&mode_25=4
        # &mode_26=4&mode_CPU=4&sid=-1

        # mirroring_ena=on&portselect=1&mode_2=3&mode_3=4&mode_4=4&mode_5=4
        # &mode_6=4&mode_7=4&mode_8=4&mode_9=4&mode_10=4&mode_11=4&mode_12=4
        # &mode_13=4&dummy=undefined&mode_14=4&mode_15=4&mode_16=4&mode_17=4
        # &mode_18=4&mode_19=4&mode_20=4&mode_21=4&mode_22=4&mode_23=4&mode_24=4
        # &mode_25=4&mode_26=4&mode_CPU=4&sid=-1

        if request.form["port_mirroring"] == "enabled":
            mirroring_ena= "on"
            portselect = request.form["destination_port"]
            data = {"mirroring_ena": mirroring_ena,
                "portselect": portselect,
                "sid": "-1"}
            response=session.post('http://'+ipaddress+'/update/config/mirroring', data=data, cookies=cookies)
        else:
            portselect = request.form["destination_port"]
            data = {"portselect": portselect,
                "sid": "-1"}
            response=session.post('http://'+ipaddress+'/update/config/mirroring', data=data, cookies=cookies)
        session.post("http://"+ipaddress+"/config/logout", cookies=cookies)
            

    
    return redirect('/ports')


# visualeditor

@app.route('/visualeditor')
@login_required
def visualeditor():
    return render_template('visualeditor.html', switches=switches.find())


# reports

@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html', reports=get_sharedfiles())


# clear download folder
@app.before_request
def clear_download_dict():
    for file in os.listdir('./download'):
        os.remove(os.path.join('./download', file))

# get switch model from ip
def get_model_from_ip(ip):
    switch = switches.find_one({ "ip": ip})
    for switchdata in switch:
        print(switchdata)
    return switch["model"] 

# flask app

if __name__ == '__main__':
    app.run(debug=1)