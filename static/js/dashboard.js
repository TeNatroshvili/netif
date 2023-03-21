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

function openSettings(ip, modalID) {
  document.getElementById(modalID).style.display = "block";
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

function closeSettings(modalID) {
  bluredBackground(false)
  document.getElementById(modalID).children[0].style.display = "block";
  document.getElementById(modalID).children[1].style.display = "none";
  document.getElementById(modalID).style.display = "none";
}

function loadSwitches() {
  refreshbutton.classList.add("refreshing")
  refreshbutton.onclick = null
  fetch(window.location.href + "/load_switches")
    .then(response => console.log(response))
    .then(nothing => {
      refreshbutton.classList.remove("refreshing")
      refreshbutton.onclick = loadSwitches
      location.reload()
    })
}

function changePassword() {
  document.getElementById("myModal2").style.display = "block";
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

      document.getElementById("username").value = userdata['username']

    }));
}

function changeSwitchPasswords() {
  document.getElementById("myModal3").style.display = "block";
  document.getElementById("myModal3").children[0].style.display = "none";
  document.getElementById("myModal3").children[1].style.display = "block";
  bluredBackground(true);
}

function submitPasswordsEncrypted() {
  old_pw = document.getElementById("old_pw").value;
  new_pw = document.getElementById("new_pw").value;
  conf_pw = document.getElementById("conf_pw").value;
  enc_old_pw = calculateDeviceID(document.getElementById("old_pw").value);
  enc_new_pw = calculateDeviceID(document.getElementById("new_pw").value);
  enc_conf_pw = calculateDeviceID(document.getElementById("conf_pw").value);

  fetch('/changeSwitchPasswords', {
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
}


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