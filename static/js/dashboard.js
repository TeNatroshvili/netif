/**********************************************
Dashboard Frontend interface
***********************************************
author:   Baumann Danièl
created:  2022-11-22
version:  1.3
***********************************************/

let modal, btn, span, header, content, footer, settings

window.onload = function () {
  modal = document.getElementById("myModal");
  modal2 = document.getElementById("myModal2");
  btn = document.getElementById("myBtn");
  span = document.getElementsByClassName("close")[0];
  header = document.getElementsByClassName("header")[0]
  content = document.getElementsByClassName("content")[0]
  footer = document.getElementsByClassName("footer")[0]
  refreshbutton = document.getElementById("refreshbutton")
}


/* open settings modal for given switch with ip adress and scrap current data from target switch */
function openSettings(ip, modalID) {
  // show modal
  document.getElementById(modalID).style.display = "block";

  // send request to backend
  fetch(window.location.href + "/scrap/" + ip)
    .then(response => {
      if (response.ok) {
        return response.json();
      } else if (response.status == 501) {
        throw new Error('Switch model not supported');
      } else {
        throw new Error('Network response was not ok');
      }
    })
    .then((settings => {
      document.getElementById(modalID).children[0].style.display = "none";
      document.getElementById(modalID).children[1].style.display = "block";
      var form = document.getElementById(modalID).getElementsByTagName("form");
      form[0].setAttribute("action", "/conf/save_system_settings/" + ip)

      bluredBackground(true)
      console.log(settings)
      document.getElementById("systemname").value = settings['system_name']
      document.getElementById("ipaddress").value = settings['ip_address']
      document.getElementById("subnetmask").value = settings['subnet_mask']
      document.getElementById("gatewayaddress").value = settings['gateway_address']
      document.getElementById("macaddress").value = settings['mac_address']
      if (settings['snmp_enalbed'] == true) {
        document.getElementById("snmp-on").checked = true;
      } else {
        document.getElementById("snmp-off").checked = true;
      }
    }));
}


/* blures or unblures the backgorund */
function bluredBackground(yes) {
  if (yes) {
    header.classList.add('blur')
    content.classList.add('blur')
    footer.classList.add('blur')
  } else {
    header.classList.remove('blur')
    content.classList.remove('blur')
    footer.classList.remove('blur')
  }
}


// close the modal
function closeSettings(modalID) {
  bluredBackground(false)
  document.getElementById(modalID).children[0].style.display = "block";
  document.getElementById(modalID).children[1].style.display = "none";
  document.getElementById(modalID).style.display = "none";
}

/* send request to backend to start the portscan */
function loadSwitches() {
  refreshbutton.classList.add("refreshing")
  refreshbutton.onclick = null
  fetch(window.location.href + "/load_switches")
    .then(response => console.log(response))
    .then(nothing => {
      // when port scan is finished remove loading animation
      refreshbutton.classList.remove("refreshing")
      refreshbutton.onclick = loadSwitches
      location.reload()
    })
}


/* show the modal to change the NETIF password  */
function changePassword() {
  document.getElementById("myModal2").style.display = "block";

  // request the userdata from the current user (only one admin currently)
  fetch(window.location.href + "/userdata")
    .then(response => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error('Network response was not ok');
      }
    })
    .then((userdata => {

      console.log("userdata")
      document.getElementById("myModal2").children[0].style.display = "none";
      document.getElementById("myModal2").children[1].style.display = "block";
      bluredBackground(true)

      // prefill the username input with the current username
      document.getElementById("username").value = userdata['username']

    }));
}


/* open modal to change all switch passwords */
function changeSwitchPasswords() {
  document.getElementById("myModal3").style.display = "block";
  document.getElementById("myModal3").children[0].style.display = "none";
  document.getElementById("myModal3").children[1].style.display = "block";
  bluredBackground(true);
}

/* send request to backend with the old password, new password and the encryped passwords versions for the 1810 switches, cause they need this */
function submitPasswordsEncrypted(event) {
  // deactivate default form request to backend
  event.preventDefault();

  // set passwords from input values
  old_pw = document.getElementById("old_pw").value;
  new_pw = document.getElementById("new_pw").value;
  conf_pw = document.getElementById("conf_pw").value;

  // encode the passwords for the 1810 switches
  enc_old_pw = calculateDeviceID(document.getElementById("old_pw").value);
  enc_new_pw = calculateDeviceID(document.getElementById("new_pw").value);
  enc_conf_pw = calculateDeviceID(document.getElementById("conf_pw").value);

  // create destination request url
  url = window.location.href.split("?")[0] + '/changeSwitchPasswords';
  
  // send request to backend
  fetch(url, {
    method: 'post',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
  },
    body: JSON.stringify({
      "old_pw": old_pw,
      "new_pw": new_pw,
      "conf_pw": conf_pw,
      "enc_old_pw": enc_old_pw,
      "enc_new_pw": enc_new_pw,
      "enc_conf_pw": enc_conf_pw
    })
  })
  .then(response => console.log(response))
  .then(none => {
    // when finish clear inputs
    document.getElementById("old_pw").value = "";
    document.getElementById("new_pw").value = "";
    document.getElementById("conf_pw").value = "";
  })
  closeSettings("myModal3")
}


/* following code is from the orignial 1810 switch password encryption which is needed to encode the passwords, so it can be changed through NETIF */

/*
Vitesse Switch Software.
Copyright (c) 2002-2013 Vitesse Semiconductor Corporation "Vitesse". All
Rights Reserved.
Unpublished rights reserved under the copyright laws of the United States of
America, other countries and international treaties. Permission to use, copy,
store and modify, the software and its source code is granted. Permission to
integrate into other products, disclose, transmit and distribute the software
in an absolute machine readable format (e.g. HEX file) is also granted.  The
source code of the software may not be disclosed, transmitted or distributed
without the written permission of Vitesse. The software and its source code
may only be used in products utilizing the Vitesse switch products.
This copyright notice must appear in any copy, modification, disclosure,
transmission or distribution of the software. Vitesse retains all ownership,
copyright, trade secret and proprietary rights in the software.
THIS SOFTWARE HAS BEEN PROVIDED "AS IS," WITHOUT EXPRESS OR IMPLIED WARRANTY
INCLUDING, WITHOUT LIMITATION, IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR USE AND NON-INFRINGEMENT.
*/
function calculateDeviceID(str) {
  let encodeChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
  var out, i, len;
  var c1, c2, c3;
  len = str.length;
  i = 0;
  out = "";
  while (i < len) {
    c1 = str.charCodeAt(i++) & 0xff;
    if (i == len) {
      out += encodeChars.charAt(c1 >> 2);
      out += encodeChars.charAt((c1 & 0x3) << 4);
      out += "==";
      break;
    }
    c2 = str.charCodeAt(i++);
    if (i == len) {
      out += encodeChars.charAt(c1 >> 2);
      out += encodeChars.charAt(((c1 & 0x3) << 4) | ((c2 & 0xF0) >> 4));
      out += encodeChars.charAt((c2 & 0xF) << 2);
      out += "=";
      break;
    }
    c3 = str.charCodeAt(i++);
    out += encodeChars.charAt(c1 >> 2);
    out += encodeChars.charAt(((c1 & 0x3) << 4) | ((c2 & 0xF0) >> 4));
    out += encodeChars.charAt(((c2 & 0xF) << 2) | ((c3 & 0xC0) >> 6));
    out += encodeChars.charAt(c3 & 0x3F);
  }
  console.log(out);
  return out;
}