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
import subprocess

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


@app.route('/dashboard/scrap')
@login_required
def scrap_settings():
    # os.chdir(os.path.dirname(__file__)+"/scrapyNetIF/scrapyNetIF")
    # process = subprocess.Popen(["scrapy", "crawl", "NetIF"])
    # process.wait()
    set = list(settings.find())
    for mydict in set:
        del mydict["_id"]
    return json.dumps(set[0])


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
    
    session.close()
    return redirect('/')


@app.route('/conf/save_port_configuration', methods=['POST'])
@login_required
def save_port_configuration():
    session = requests.Session()
    response = session.post('http://10.137.4.41/htdocs/login/login.lua', data=switch_login_credentials)

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
    response = session.post('http://10.137.4.41/htdocs/login/login.lua', data=switch_login_credentials)

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


@app.route('/conf/save_port_mirroring', methods=['POST'])
@login_required
def save_port_mirroring():
    session = requests.Session()
    response = session.post('http://10.137.4.41/htdocs/login/login.lua', data=switch_login_credentials)

    #port_mirroring_sel%5B%5D=enabled&destination_port_sel%5B%5D=1&sorttable1_length=-1&b_form1_submit=Apply&b_form1_clicked=b_form1_submit
    port_mirroring = request.form["port_mirroring_sel[]"]
    destination_port = request.form["destination_port_sel[]"]

    data = {"port_mirroring_sel[]": port_mirroring,
            "destination_port_sel[]": destination_port,
            "sorttable1_length": "-1",
            "b_form1_submit": "Apply",
            "b_form1_clicked": "b_form1_submit"}
    
    response = session.post("http://10.137.4.41/htdocs/pages/base/port_mirror.lsp", data=data, cookies=session.cookies.get_dict())
    session.post("http://10.137.4.41/htdocs/lua/ajax/save_cfg.lua?save=1", cookies=session.cookies.get_dict())
    session.get("http://10.137.4.41/htdocs/pages/main/logout.lsp", cookies=session.cookies.get_dict())
    
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
    return render_template('reports.html')


# clear download folder
@app.before_request
def clear_download_dict():
    for file in os.listdir('./download'):
        os.remove(os.path.join('./download', file))


# flask app

if __name__ == '__main__':
    app.run()