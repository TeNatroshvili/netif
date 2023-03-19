let modal, btn, span, header, content, footer, settings

let currentIP

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
  currentIP = ip
  fetch(window.location.href + "/scrap/"+ip)
      .then(response => {
          if (response.ok) {
              return response.json();
          } else if(response.status == 501){
            throw new Error('Switch model not supported');
          }else {
              throw new Error('Network response was not ok');
          }
      })
      .then((settings => {
          document.getElementById(modalID).children[0].style.display = "none";
          document.getElementById(modalID).children[1].style.display = "block";
          bluredBackground(true)
          console.log(settings)
          document.getElementById("systemname").value = settings['system_name']
          document.getElementById("ipaddress").value = settings['ip_address']
          document.getElementById("subnetmask").value = settings['subnet_mask']
          document.getElementById("gatewayaddress").value = settings['gateway_address']
          document.getElementById("macaddress").value = settings['mac_address']
          if(settings['snmp_enalbed'] == true){
            document.getElementById("snmp-on").checked = true;
          }else{
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
  currentIP = null;
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

function changePassword(){
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

function saveData(){
  fetch('https://httpbin.org/post', {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({a: 1, b: 'Textual content'})
  });
}