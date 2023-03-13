var modal, btn, span, header, content, footer, settings
window.onload = function () {
  modal = document.getElementById("myModal");
  btn = document.getElementById("myBtn");
  span = document.getElementsByClassName("close")[0];
  header = document.getElementsByClassName("header")[0]
  content = document.getElementsByClassName("content")[0]
  footer = document.getElementsByClassName("footer")[0]
  refreshbutton = document.getElementById("refreshbutton")
}

function openSettings(ip) {
  modal.style.display = "block";
  fetch(window.location.href + "scrap")
    .then(response => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error('Network response was not ok');
      }
    })
    .then((settings => {
      modal.children[0].style.display = "none";
      modal.children[1].style.display = "block";
      bluredBackground(true)

      document.getElementById("systemname").value = settings['system_name'][0]
      document.getElementById("serialnumber").value = settings['serial_number'][0]
      document.getElementById("ipadress").value = settings['ip_adresse'][0]
      document.getElementById("subnetmask").value = settings['subnet_mask'][0]
      document.getElementById("gatewayadress").value = settings['gateway_ip'][0]
      document.getElementById("macadress").value = settings['mac_adreese'][0]
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
  fetch(window.location.href + "load_switches")
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