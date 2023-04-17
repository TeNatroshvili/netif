/**********************************************
Drag and Drop Field for Visual Editor
***********************************************
author:   Baumann Danièl
created:  2022-12-21
version:  1.3
***********************************************/

var switches;
var canvas, stage;

var mouseTarget; // the display object currently under the mouse, or being dragged
var dragStarted; // indicates whether we are currently in a drag operation
var offset;
var update = true;

var container = new createjs.Container();

/* Hide the Shape with the given id */
function hideShapeById(shape_id) {
    // search for the shape with the given id in a list with all shapes 
    // and hide the one with the same id as given
    // when id found set update to true, so the stage will be automatically updated
    container.children.forEach(shape => {
        if (shape.id == shape_id) {
            update = true;
            shape.visible = !document.getElementById('eye-' + shape_id).checked;
        }
    });
}

window.onload = function () {
    switches = document.getElementsByClassName('switch-list-item-ip');
    switches_names = document.getElementsByClassName('switch-list-item-name');
    // create stage and point it to the canvas:
    canvas = document.getElementById("switchField");
    stage = new createjs.Stage(canvas);

    // enable touch interactions if supported on the current device:
    createjs.Touch.enable(stage);

    // enabled mouse over / out events
    // stage.enableMouseOver(10);
    stage.mouseMoveOutside = true; // keep tracking the mouse even when it leaves the canvas

    // load the source image:
    var image = new Image();
    image.src = "../static/images/switch.png";
    image.onload = handleImageLoad;
}

function handleImageLoad(event) {
    var image = event.target;
    var shape;
    // inital first position
    var posx = 10;
    var posy = 10;

    stage.addChild(container);

    for (var i = 0; i < switches.length; i++) {
        // create the shape and add the image to the container
        shape = new createjs.Container()
        shape.id = switches[i].innerHTML
        bitmap = new createjs.Bitmap(image)
        bitmap.border
        bitmap.width = shape.height = 100;
        
        // add the switch name under the image
        var text = new createjs.Text(switches_names[i].innerHTML, "20px Arial");
        text.y = 110
        shape.addChild(bitmap)
        shape.addChild(text)

        // set the inital position of the switch images next to each other
        // when stored infrastructure is loaded this should be in a if else block
        shape.x = posx;
        shape.y = posy;
        posx = posx + 110;

        // add shape to the container
        container.addChild(shape);


        // the mousedown event stores the current positon of the clicked shape
        shape.on("mousedown", function (evt) {
            this.parent.addChild(this);
            this.offset = {
                x: this.x - evt.stageX,
                y: this.y - evt.stageY
            };
        });

        // the pressmove event is dispatched when the mouse moves after a mousedown on the target until the mouse is released
        // and updates the curretn position of the shape while is draged by the mouse
        shape.on("pressmove", function (evt) {
            this.x = evt.stageX + this.offset.x;
            this.y = evt.stageY + this.offset.y;
            // indicate that the stage should be updated
            update = true;
        });


        // eventlistener for "mouse over" event
        // currently nothing happens visually
        shape.on("rollover", function (evt) {
            this.scale = this.originalScale;
            // indicate that the stage should be updated
            update = true;
        });


        // eventlistener for "mouse out" event
        // currently nothing happens visually
        shape.on("rollout", function (evt) {
            this.scale = this.originalScale;
            // indicate that the stage should be updated
            update = true;
        });
    }

    // when shae should be not visible when initialy loaded, its set to not visible
    // for example when the stored infrastructure includes some unvisibly shapes
    container.children.forEach(shape => {
        console.log(shape.id)
        if(shape.id != null){
            update = true;
            shape.visible = !document.getElementById('eye-' + shape.id).checked; 
        }
      });

    // add eventlistener for tick anb enable automatic stage updateing
    createjs.Ticker.addEventListener("tick", tick);
}

/* When the update variable is True, the stage will be updated */
function tick(event) {
    // this set makes it so the stage only re-renders when an event handler indicates a change has happened.
    if (update) {
        update = false; // only update once
        stage.update(event);
    }
}

/* Stop the EventListener for the tick event and stop the automatic stage update function */
function stop() {
    createjs.Ticker.removeEventListener("tick", tick);
}