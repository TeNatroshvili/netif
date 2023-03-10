var switches;
var canvas, stage;

var mouseTarget; // the display object currently under the mouse, or being dragged
var dragStarted; // indicates whether we are currently in a drag operation
var offset;
var update = true;

var container = new createjs.Container();

function hideShapeById(shape_id) {
    container.children.forEach(shape => {
        if (shape.id == shape_id) {
            update = true;
            shape.visible = !document.getElementById('eye-' + shape_id).checked;
        }
    });
}

window.onload = function () {
    switches = document.getElementsByClassName('switch-list-item-ip');
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

function stop() {
    createjs.Ticker.removeEventListener("tick", tick);
}

function handleImageLoad(event) {
    var image = event.target;
    var shape;
    var posx = 10;
    var posy = 10;

    stage.addChild(container);

    for (var i = 0; i < switches.length; i++) {
        shape = new createjs.Container()
        shape.id = switches[i].innerHTML
        bitmap = new createjs.Bitmap(image)
        bitmap.border
        bitmap.width = shape.height = 100;
        var text = new createjs.Text(switches[i].innerHTML, "17px Arial");
        text.y = 110
        shape.addChild(bitmap)
        shape.addChild(text)

        shape.x = posx;
        shape.y = posy;
        posx = posx + 110;
        container.addChild(shape);


        // using "on" binds the listener to the scope of the currentTarget by default
        // in this case that means it executes in the scope of the button.
        shape.on("mousedown", function (evt) {
            this.parent.addChild(this);
            this.offset = {
                x: this.x - evt.stageX,
                y: this.y - evt.stageY
            };
        });

        // the pressmove event is dispatched when the mouse moves after a mousedown on the target until the mouse is released.
        shape.on("pressmove", function (evt) {
            this.x = evt.stageX + this.offset.x;
            this.y = evt.stageY + this.offset.y;
            // indicate that the stage should be updated on the next tick:
            update = true;
        });

        shape.on("rollover", function (evt) {
            this.scale = this.originalScale;
            update = true;
        });

        shape.on("rollout", function (evt) {
            this.scale = this.originalScale;
            update = true;
        });



    }

    container.children.forEach(shape => {
        update = true;
        shape.visible = !document.getElementById('eye-' + shape.id).checked;
    });

    createjs.Ticker.addEventListener("tick", tick);
}

function tick(event) {
    // this set makes it so the stage only re-renders when an event handler indicates a change has happened.
    if (update) {
        update = false; // only update once
        stage.update(event);
    }
}