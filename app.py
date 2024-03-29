# ---------------------------------------------------------
# Flask Interface
# ---------------------------------------------------------
# author:   Baumann Danièl
# created:  2022-11-22
# version:  2.3
# ---------------------------------------------------------

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
    users,
    update_switch_ip,
    get_switch_credentials,
    update_switch_credentials
)
from samba import (
    get_sharedfiles,
    download,
    upload
)
from switch_detection import search_switches
from model import User
from scraping_1810 import scrap_switch_1810
from scraping_1820 import scrap_switch_1820

import requests

# login manager for the user authentification
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"

app = Flask(__name__)
login_manager.init_app(app)
app.secret_key = os.urandom(43)

# user loader
@login_manager.user_loader
def load_user(user_id):
    user = User.get_by_id(user_id)
    if user is not None:
        return user
    else:
        return None


# login page route
@app.get("/login")
def login_page():
    return render_template("login.html")


# before every request reset the session timeout to 15 minutes
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)
    session.modified = True
    g.user = current_user


# login post request
@app.post("/login")
def login():
    # get username and password from request
    username = request.form["username"]
    password = request.form["password"]

    # find the user by username
    find_user = users.find_one({"username": username})

    # validate user and login when successful
    if User.login_valid(username, password):
        loguser = User(find_user["username"],
                       find_user["password"], find_user["_id"])
        login_user(loguser)
        flash('You have been logged in!', 'success')
        next = request.args.get('next')
        return redirect(next or url_for('dashboard'))
    else:
        flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template("login.html")


# logout route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("succesfully loged out", "success")
    return redirect(url_for("login"))


# post request for NETIF user password change
@app.route("/changePassword", methods=["POST"])
@login_required
def changePassword():
    # get data from request
    username = request.form["username"]
    password = request.form["password"]
    newpass = request.form["newpass"]

    # when successful redirect to login and clear session
    if User.change_password(username, password, newpass):
        flash("succesfully changed admin password", "success")
        session.clear()
        return redirect(url_for("login"))
    else:
        flash('password change for admin was unsuccessful.', 'danger')
        return redirect(url_for("dashboard"))


# default route redirect dashboard route
@app.route("/")
@login_required
def default():
    return redirect(url_for("dashboard"))


# dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', switches=switches.find(), reports=get_sharedfiles())


# request to get the current userdata as json
@app.route("/dashboard/userdata", methods=["GET"])
@login_required
def userdata():
    user = users.find_one({"_id": session["_user_id"]})
    return {"username": user["username"]}


# request to beginn scraping script with ip of the 
# target switch as request paramter and return current settings after
@app.route('/dashboard/scrap/<ip>')
@login_required
def scrap_settings(ip):
    # get the model from the target switch
    model = get_model_from_ip(ip)

    # check which model it is to call the correct scraping script
    if ("1810" in model):
        scrap_switch_1810(ip)
    elif ("1820" in model):
        scrap_switch_1820(ip)
    else:
        print("Switch Model not supported")
        return 'not supported', 501

    setting = settings.find_one({"ip_address": ip})
  
    # remove the _id field which is automatically created by mongodb
    # it would cause errors in the javascript json object later
    if("_id" in setting):
        del setting["_id"]
    return json.dumps(setting)


# route to call the portscan script
@app.route('/dashboard/load_switches')
@login_required
def load_switches():
    return search_switches()


# ports route
@app.route('/ports')
@login_required
def ports():
    return render_template('ports.html', switches=switches.find())



# request to beginn scraping script with ip of the 
# target switch as request paramter and return current settings after
@app.route('/ports/scrap/<ip>')
@login_required
def scrap_port_settings(ip):
    # get the model from the target switch
    model = get_model_from_ip(ip)
    
    # check which model it is to call the correct scraping script
    if ("1810" in model):
        scrap_switch_1810(ip)
    elif ("1820" in model):
        scrap_switch_1820(ip)
    else:
        print("Switch Model not supported")
        return 'not supported', 501

    setting = settings.find_one({"ip_address": ip})
  
    
    # remove the _id field which is automatically created by mongodb
    # it would cause errors in the javascript json object later
    if("_id" in setting):
        del setting["_id"]
    return json.dumps(setting)


# route to download the report file from the fileserver with the filename as reuqest parameter
# and automatically open the download dialog in the frontend when pop ups are not blocked by the browser
@app.route('/download/<filename>')
@login_required
def download_file(filename):
    return send_file(download(filename), as_attachment=True)


# configuration post request to save the changes made in the frontend
@app.route('/conf/save_system_settings/<ip>', methods=['POST'])
@login_required
def save_system_settings(ip):
    # get data from request
    ipaddress = request.form["ipaddress"]
    subnetmask = request.form["subnetmask"]
    gatewayaddress = request.form["gatewayaddress"]
    name = request.form["systemname"]
    snmp = request.form["snmp"]

    # get the model from the ip adress
    model = get_model_from_ip(ip)
    
    # check which model it is to make the correct http request to the target switch 
    if ("1810" in model):

        # open session and get the cookies information
        session = requests.Session()
        session.post('http://'+ipaddress+'/config/login',
                     data=get_switch_credentials()["password"])
        seid_cookie = session.cookies.get_dict()
        seid_cookie_str = '; '.join(
            [f'{key}={value}' for key, value in seid_cookie.items()])
        cookies = {'seid': seid_cookie_str,
                   'deviceid': 'YWRtaW46U3lwMjAyM2h1cnJh'}

        # create the data result dictionary
        data = {"sys_name": name}

        # send the post request to the switch
        session.post("http://"+ip+"/update/config/sysinfo",
                     data=data, cookies=cookies)

        # create a new data result dictornary
        data = {"ip_addr": ipaddress,
                "ip_mask": subnetmask,
                "gateway_addr": gatewayaddress}

        if (snmp == "on"):
            data["snmp_mode"] = "on"

        # send the post request to the switch
        session.post("http://"+ip+"/update/config/ip_config",
                     data=data, cookies=cookies)

        # logout from the switch
        session.post("http://"+ip+"/config/logout", cookies=cookies)
    elif ("1820" in model):
        # create new session and get cookies
        session = requests.Session()
        session.post('http://'+ip+'/htdocs/login/login.lua',
                     data=get_switch_credentials())

        # create a new data result dictornary
        data = {"sys_name": name,
                "b_form1_submit": "Apply",
                "b_form1_clicked": "b_form1_submit"}

        # send post request to target switch and call the save button
        session.post("http://"+ip+"/htdocs/pages/base/dashboard.lsp",
                     data=data, cookies=session.cookies.get_dict())
        session.post("http://"+ip+"/htdocs/lua/ajax/save_cfg.lua?save=1",
                     cookies=session.cookies.get_dict())

        # create new data dictionary
        data = {"protocol_type_sel[]": "static",
                "ip_addr": ipaddress,
                "subnet_mask": subnetmask,
                "gateway_address": gatewayaddress,
                "session_timeout": "5",
                "mgmt_vlan_id_sel[]": "1",
                "mgmt_port_sel[]": "none", }

        if (snmp == "on"):
            data.update({"snmp_sel[]": "enabled",
                         "community_name": "public"})
        elif (snmp == "off"):
            data.update({"snmp_sel[]": "disabled"})
        data.update({"b_form1_submit": "Apply",
                     "b_form1_clicked": "b_form1_submit"})

        # send the post request to the target switch and call the save button
        session.post("http://"+ip+"/htdocs/pages/base/network_ipv4_cfg.lsp",
                     data=data, cookies=session.cookies.get_dict())
        session.post("http://"+ip+"/htdocs/lua/ajax/save_cfg.lua?save=1",
                     cookies=session.cookies.get_dict())
        
        # logout from switch
        session.get("http://"+ip+"/htdocs/pages/main/logout.lsp",
                    cookies=session.cookies.get_dict())
    else:
        print("Switch Model not supported")

    # when switch ip has been changed, change it in switches collections
    if (ip != ipaddress):
        update_switch_ip(ip, ipaddress)

    return redirect('/')


@app.route('/dashboard/changeSwitchPasswords', methods=["POST"])
@login_required
def update_passwords():
    # get all data from request
    old_pw = request.json["old_pw"]
    new_pw = request.json["new_pw"]
    conf_pw = request.json["conf_pw"]
    enc_old_pw = request.json["enc_old_pw"]
    enc_new_pw = request.json["enc_new_pw"]
    enc_conf_pw = request.json["enc_conf_pw"]

    for switch in switches.find():
        ip = switch["ip"]
        # get the model from the ip
        model = get_model_from_ip(ip)

        # check which model it is
        if ("1820" in model):
            # get cookies
            session = requests.Session()
            session.post(
                'http://'+ip+'/htdocs/login/login.lua', data=get_switch_credentials())

            # create data dictionary
            data = {"user_name": "admin",
                    "current_password": old_pw,
                    "new_password": new_pw,
                    "confirm_new_passwd": conf_pw,
                    "b_form1_submit": "Apply",
                    "b_form1_clicked": "b_form1_submit"}

            # send post request to target switch and call save butotn
            session.post("http://"+ip+"/htdocs/pages/base/user_accounts.lsp",
                                    data=data, cookies=session.cookies.get_dict())
            session.post("http://"+ip+"/htdocs/lua/ajax/save_cfg.lua?save=1",
                         cookies=session.cookies.get_dict())
            
            # logout from switch
            session.get("http://"+ip+"/htdocs/pages/main/logout.lsp",
                        cookies=session.cookies.get_dict())
            
            print("changed pw for: "+ip)

        elif ("1810" in model):
            # get cookeis
            session = requests.Session()
            response = session.post(
                'http://'+ip+'/config/login', data=get_switch_credentials()["password"])
            seid_cookie = session.cookies.get_dict()

            seid_cookie_str = '; '.join(
                [f'{key}={value}' for key, value in seid_cookie.items()])
            cookies = {'seid': seid_cookie_str,
                       'deviceid': 'YWRtaW46U3lwMjAyM2h1cnJh'}

            # create data dictionary
            data = {"oldpass": enc_old_pw,
                    "pass1": enc_new_pw,
                    "pass2": enc_conf_pw}

            # send post request to switch
            session.post('http://'+ip+'/update/config/passwd',
                         data=data, cookies=cookies)

            # logout from switch
            session.post("http://"+ip+"/config/logout", cookies=cookies)

            print("changed pw for: "+ip)

        # update the new password in the credentials collection
        update_switch_credentials(new_pw)

    return redirect(url_for("dashboard"))


# route for port configuration
@app.route('/conf/save_port_configuration/<ipaddress>', methods=['POST'])
@login_required
def save_port_configuration(ipaddress):
    # Get the switch model from its IP address
    model = get_model_from_ip(ipaddress)

    # If the switch model contains "1820"
    if ("1820" in model):
        # Create a new session and log in to the switch
        session = requests.Session()
        response = session.post(
            'http://'+ipaddress+'/htdocs/login/login.lua', data=get_switch_credentials())

        # Get form data from the HTTP request
        admin_mode = request.form["admin_mode"]
        phys_mode = request.form["phys_mode"]
        port_descr = request.form["port_descr"]
        intf = request.form["intf"]

        # Set the data to be sent in the POST request to the switch
        data = {"admin_mode_sel[]": admin_mode,
                "phys_mode_sel[]": phys_mode,
                "port_descr": port_descr,
                "intf": intf,
                "b_modal1_clicked": "b_modal1_submit"}

        # Send the POST request to the switch to update the port configuration
        response = session.post("http://"+ipaddress+"/htdocs/pages/base/port_summary_modal.lsp",
                                data=data, cookies=session.cookies.get_dict())
        
        # Save the updated switch configuration
        session.post("http://"+ipaddress+"/htdocs/lua/ajax/save_cfg.lua?save=1",
                     cookies=session.cookies.get_dict())
        
        # Log out of the switch
        session.get("http://"+ipaddress+"/htdocs/pages/main/logout.lsp",
                    cookies=session.cookies.get_dict())

    # If the switch model contains "1810"
    elif ("1810" in model):
        # Create a new session and log in to the switch
        session = requests.Session()
        response = session.post(
            'http://'+ipaddress+'/config/login', data=get_switch_credentials()["password"])
        seid_cookie = session.cookies.get_dict()

        # Convert the session ID cookie to a string format
        seid_cookie_str = '; '.join(
            [f'{key}={value}' for key, value in seid_cookie.items()])
        
        # Set the cookies to be sent in the POST request to the switch
        cookies = {'seid': seid_cookie_str,
                   'deviceid': 'YWRtaW46U3lwMjAyM2h1cnJh'}

        # Get form data from the HTTP request
        speed_id = request.form["phys_mode"]
        port = request.form["intf"]

        # Set the speed parameter based on the selected option
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

        # If the port admin mode is enabled
        if request.form["admin_mode"] == "enabled":
            admin = "on"

            # Set the data to be sent in the POST request to the switch
            data = {"port": port,
                    "admin": admin,
                    "speed": speed,
                    "sid": "-1"}
            
            # Send the POST request to the switch to update the port configuration
            session.post('http://'+ipaddress+'/update/config/ports',
                         data=data, cookies=cookies)
        else:
            # Set the data to be sent in the POST request to the switch
            data = {"port": port,
                    "speed": speed,
                    "sid": "-1"}
            
            # Send the POST request to the switch to update the port configuration
            session.post('http://'+ipaddress+'/update/config/ports',
                         data=data, cookies=cookies)

        # Log out of the switch
        session.post("http://"+ipaddress+"/config/logout", cookies=cookies)

    # redirect to the ports page
    return redirect('/ports')


# post request for all port configuration
@app.route('/conf/save_all_port_configuration/<ipaddress>', methods=['POST'])
@login_required
def save_all_port_configuration(ipaddress):
    # create a new session
    session = requests.Session()
    
    # send a POST request to login to the switch
    response = session.post(
        'http://'+ipaddress+'/htdocs/login/login.lua', data=get_switch_credentials())

    # get the physical mode and port description from the form
    phys_mode = request.form["phys_mode"]
    port_descr = request.form["port_descr"]

    # Set the data to be sent in the POST request to the switch
    data = {"phys_mode_sel[]": phys_mode,
            "port_descr": port_descr,
            "intf": "all",
            "b_modal1_clicked": "b_modal1_submit"}

    # send a POST request to save the port configuration
    response = session.post("http://"+ipaddress+"/htdocs/pages/base/port_summary_modal.lsp",
                            data=data, cookies=session.cookies.get_dict())
    
    # send a POST request to save the configuration
    session.post("http://"+ipaddress+"/htdocs/lua/ajax/save_cfg.lua?save=1",
                 cookies=session.cookies.get_dict())
    
    # Log out of the switch
    session.get("http://"+ipaddress+"/htdocs/pages/main/logout.lsp",
                cookies=session.cookies.get_dict())

    # redirect to the ports page
    return redirect('/ports')


# post request for port mirroring configuration
@app.route('/conf/save_port_mirroring/<ipaddress>', methods=['POST'])
@login_required
def save_port_mirroring(ipaddress):
    # Get the switch model from its IP address
    model = get_model_from_ip(ipaddress)

    # If the switch model contains "1820"
    if ("1820" in model):
        # Create a new session and log in to the switch
        session = requests.Session()
        response = session.post(
            'http://'+ipaddress+'/htdocs/login/login.lua', data=get_switch_credentials())

        # Get form data from the HTTP request
        port_mirroring = request.form["port_mirroring"]
        destination_port = request.form["destination_port"]
        source_port = request.form["source_port"]
        direction = request.form["direction"]

        # Set the data to be sent in the POST request to the switch
        data = {"port_mirroring_sel[]": port_mirroring,
                "destination_port_sel[]": destination_port,
                "sorttable1_length": "-1",
                "b_form1_submit": "Apply",
                "b_form1_clicked": "b_form1_submit"}

        # Send the data to the switch
        response = session.post("http://"+ipaddress+"/htdocs/pages/base/port_mirror.lsp",
                                data=data, cookies=session.cookies.get_dict())
        
        # Save the switch configuration
        session.post("http://"+ipaddress+"/htdocs/lua/ajax/save_cfg.lua?save=1",
                     cookies=session.cookies.get_dict())
        
        # Log out of the switch
        session.get("http://"+ipaddress+"/htdocs/pages/main/logout.lsp",
                    cookies=session.cookies.get_dict())
    
    # If the switch model contains "1810"
    elif ("1810" in model):
        # Create a new session and log in to the switch
        session = requests.Session()
        response = session.post(
            'http://'+ipaddress+'/config/login', data=get_switch_credentials()["password"])
        seid_cookie = session.cookies.get_dict()

        # Convert the session ID cookie to a string format
        seid_cookie_str = '; '.join(
            [f'{key}={value}' for key, value in seid_cookie.items()])
        
        # Set the cookies to be sent in the POST request to the switch
        cookies = {'seid': seid_cookie_str,
                   'deviceid': 'YWRtaW46U3lwMjAyM2h1cnJh'}

        # Get the port mirroring and destination port values from the request
        if request.form["port_mirroring"] == "enabled":
            mirroring_ena = "on"
            portselect = request.form["destination_port"]
            
            # Set the data to be sent in the POST request to the switch
            data = {"mirroring_ena": mirroring_ena,
                    "portselect": portselect,
                    "sid": "-1"}
            
            # Send the data to the switch
            response = session.post(
                'http://'+ipaddress+'/update/config/mirroring', data=data, cookies=cookies)
        else:
            portselect = request.form["destination_port"]
            
            # Set the data to be sent in the POST request to the switch
            data = {"portselect": portselect,
                    "sid": "-1"}
            
            # Send the data to the switch
            response = session.post(
                'http://'+ipaddress+'/update/config/mirroring', data=data, cookies=cookies)
        
        # Log out of the switch
        session.post("http://"+ipaddress+"/config/logout", cookies=cookies)

    # redirect to the ports page
    return redirect('/ports')


# visualeditor route
@app.route('/visualeditor')
@login_required
def visualeditor():
    return render_template('visualeditor.html', switches=switches.find())


# reports route
@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html', reports=get_sharedfiles())


# clear download folder before every request
@app.before_request
def clear_download_dict():
    for file in os.listdir('./download'):
        if (str(file).endswith(".gitkeep") != True):
            os.remove(os.path.join('./download', file))


# get switch model from ip
def get_model_from_ip(ip):
    switch = switches.find_one({"ip": ip})
    return switch["model"]

# flask app
if __name__ == '__main__':
    app.run(debug=1)