/**********************************************
Port configuration
***********************************************
author:   Baumann Danièl
created:  2023-02-28
version:  1.1
***********************************************/

var modal, btn, span, header, content, footer, settings


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
            } else {
                throw new Error('Network response was not ok');
            }
        })
        .then((settings => {
            document.getElementById(modalID).children[0].style.display = "none";
            document.getElementById(modalID).children[1].style.display = "block";
            bluredBackground(true)

            // TODO
            // here should the inputs in the frontend be prefilled with the data from the returned settings json object

        }));
}

// function configureAllIntf(modalID) {
//     document.getElementById(modalID).style.display = "block";
//     fetch(window.location.href + "/scrap")
//         .then(response => {
//             if (response.ok) {
//                 return response.json();
//             } else {
//                 throw new Error('Network response was not ok');
//             }
//         })
//         .then((settings => {
//             document.getElementById(modalID).children[0].style.display = "none";
//             document.getElementById(modalID).children[1].style.display = "block";
//             bluredBackground(true)

//             // TODO
//             // here should the inputs in the frontend be prefilled with the data from the returned settings json object
//         }));
// }


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