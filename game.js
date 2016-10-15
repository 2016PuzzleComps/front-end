var vehicleColor = '#0000FF';
var vipColor = '#FF0000';
var squareSize = 100;
var board;

function Board(width, height, exit) {
	this.width = width;
	this.height = height;
	this.vehicles = [];
	this.exit = exit;
}

function Exit(cardinal, offset) {
	this.cardinal = cardinal;
	this.offset = offset;
}

Board.prototype.addVehicle = function(v) {
	this.vehicles.push(v);
}

function Vehicle(isVip, horiz, size, x, y) {
	this.isVip = isVip;
	this.horiz = horiz;
	this.size = size;
	this.x = x;
	this.y = y;
}

function handleFileSelect(evt) {
	var files = evt.target.files; // FileList object

	// files is a FileList of File objects. List some properties.
	var output = [];
	var file = files[0];
	var reader = new FileReader();

	// If we use onloadend, we need to check the readyState.
	reader.onloadend = function(evt) {
		if (evt.target.readyState == FileReader.DONE) { // DONE == 2
			var lines = evt.target.result.split("\n");
			var dimen = lines[0].split(" ");
			var exitPos = lines[1].split(" ");
			board = new Board(dimen[0], dimen[1],
				new Exit(exitPos[0],exitPos[1]));
			var isFirst = true;
			for (var i=2; i<lines.length; i++) {
				var items = lines[i].split(" ");
				if (items.length != 4) {
					break;
				}
				var newVehicle = new Vehicle(isFirst, items[3].charAt(0)=="T", items[2], items[0],items[1]);
				board.vehicles.push(newVehicle);
				if (isFirst) {
					isFirst = false;
				}
			}
			drawFrame();	
		}
	};
	reader.readAsText(file);
}
document.getElementById('files').addEventListener('change', handleFileSelect, false);

function drawVehicle(vehicle) {
	context.beginPath();
	if(vehicle.horiz) {
		context.rect(vehicle.x * squareSize + 1, vehicle.y * squareSize + 1, vehicle.length * squareSize - 2, squareSize - 2);
	} else {
		context.rect(vehicle.x * squareSize + 1, vehicle.y * squareSize + 1, squareSize - 2, vehicle.length * squareSize - 2);
	}
	if(vehicle.isVip) {
		context.fillStyle = vipColor;
	} else {
		context.fillStyle = vehicleColor;
	}
	context.fill();
	context.closePath();
}

function drawFrame() {
	// clear everything
	context.clearRect(0, 0, canvas.width, canvas.height);
	// draw board grid
	for(var i = 0; i <= board.width; i++) {
		context.moveTo(0, (i * squareSize));
		context.lineTo(board.width * squareSize, (i * squareSize));
		context.stroke();
	}
	for(var i = 0; i <= board.height; i++) {
		context.moveTo((i * squareSize), 0);
		context.lineTo((i * squareSize), board.height * squareSize);
		context.stroke();
	}
	// clear exit
	if(board.exit.cardinal == 'E') {
		context.clearRect((board.width * squareSize) - 1, (board.exit.offset * squareSize) + 1, squareSize - 2, squareSize - 2);
	}
	// draw vehicles
	for(i in board.vehicles) {
		drawVehicle(board.vehicles[i]);
	}
}

var canvas = document.getElementById("gameCanvas");
var context = canvas.getContext("2d");

/* MOUSE EVENTS */

// index of vehicle in board.vehicles that is selected by mouse 
var selectedVehicleIndex = null;
var mouseOffset = 0;

// get position of mouse at a mouse event
function getMousePos(e) {
	var rect = canvas.getBoundingClientRect();
	return {
		x: e.clientX - rect.left,
		y: e.clientY - rect.top
	};
}

// mousedown
canvas.addEventListener('mousedown', function(e) {
	var mousePos = getMousePos(e);
	// find if mouse is over a vehicle on the board
	for(i in board.vehicles) {
		var v = board.vehicles[i];
		if((v.horiz == true) && (v.x * squareSize <= mousePos.x) && (mousePos.x <= (v.x + v.size) * squareSize) && (v.y * squareSize <= mousePos.y) && (mousePos.y <= (v.y + 1) * squareSize)) {
			selectedVehicleIndex = i;
			mouseOffset = mousePos.x - (v.x * squareSize);
			return;
		}
		if((v.horiz == false) && (v.x * squareSize <= mousePos.x) && (mousePos.x <= (v.x + 1) * squareSize) && (v.y * squareSize <= mousePos.y) && (mousePos.y <= (v.y + v.size) * squareSize)) {
			selectedVehicleIndex = i;
			mouseOffset = mousePos.y - (v.y * squareSize);
			return;
		}
	}
});

// mousemove
canvas.addEventListener('mousemove', function(e) {
	var mousePos = getMousePos(e);
	if(selectedVehicleIndex != null) {
		var selectedVehicle = board.vehicles[selectedVehicleIndex];
		var blocked = false;
		if(selectedVehicle.horiz) {
			var newX = (mousePos.x - mouseOffset) / squareSize;
			// see if anything is blocking
			// first check walls
			if(newX < 0) {
				selectedVehicle.x = 0;
				blocked = true;
			} else if(newX + selectedVehicle.size > board.width) {
				selectedVehicle.x = board.width - selectedVehicle.size;
				blocked = true;
			} else {
				// then check vehicles
				for(i in board.vehicles) {
					// skip selected vehicle
					if(i == selectedVehicleIndex) {
						continue;
					}
					var otherVehicle = board.vehicles[i];
					// if other vehicle is horizontal or not
					if(otherVehicle.horiz) {
						if(otherVehicle.y == selectedVehicle.y) {
							// which side of selected vehicle is other vehicle on
							if(newX < otherVehicle.x && newX + selectedVehicle.size > otherVehicle.x && newX > selectedVehicle.x) {
								selectedVehicle.x = otherVehicle.x - selectedVehicle.size;
								blocked = true;
								break;
							} 
							if(newX > otherVehicle.x && newX <= otherVehicle.x + otherVehicle.size && newX < selectedVehicle.x) {
								selectedVehicle.x = otherVehicle.x + otherVehicle.size;
								blocked = true;
								break;
							}
						}
					} else {
						if(otherVehicle.x == selectedVehicle.x) {
						}
					}
				}
				if(!blocked) {
					// move vehicle
					selectedVehicle.x = newX;
				}
			}
		} else {
			var newY = (mousePos.y - mouseOffset) / squareSize;
			// see if anything is blocking
			// move vehicle
			selectedVehicle.y = newY;
		}
		drawFrame();
	}
});

// mousedown
canvas.addEventListener('mouseup', function(e) {
	var selectedVehicle = board.vehicles[selectedVehicleIndex];
	// snap selected vehicle to nearest spot
	if(selectedVehicle.horiz) {
		selectedVehicle.x = Math.round(selectedVehicle.x);
	} else {
		selectedVehicle.y = Math.round(selectedVehicle.y);
	}
	// draw frame
	drawFrame();
	// deselect vehicle
	selectedVehicleIndex = null;
});



/* TESTING */
var board = new Board(6, 6, new Exit('E', 2));

board.addVehicle(new Vehicle(false, true, 3, 0, 0));
board.addVehicle(new Vehicle(true, true, 2, 4, 0));

drawFrame();
