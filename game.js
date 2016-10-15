var vehicleColor = '#0000FF'
var vipColor = '#FF0000'
var squareSize = 100

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

function drawVehicle(vehicle) {
	context.beginPath();
	if(vehicle.horiz) {
		context.rect(vehicle.x * squareSize, vehicle.y * squareSize, vehicle.size * squareSize, squareSize);
	} else {
		context.rect(vehicle.x * squareSize, vehicle.y * squareSize, squareSize, vehicle.size * squareSize);
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
var selectedVehicle = null;
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
			selectedVehicle = v;
			mouseOffset = mousePos.x - (v.x * squareSize);
			return;
		}
		if((v.horiz == false) && (v.x * squareSize <= mousePos.x) && (mousePos.x <= (v.x + 1) * squareSize) && (v.y * squareSize <= mousePos.y) && (mousePos.y <= (v.y + v.size) * squareSize)) {
			selectedVehicle = v;
			mouseOffset = mousePos.y - (v.y * squareSize);
			return;
		}
	}
});

// mousemove
canvas.addEventListener('mousemove', function(e) {
	var mousePos = getMousePos(e);
	if(selectedVehicle != null) {
		if(selectedVehicle.horiz) {
			var newX = (mousePos.x - mouseOffset) / squareSize;
			// see if anything is blocking
			// first check walls
			if(newX < 0) {
				selectedVehicle.x = 0;
			} else if(newX + selectedVehicle.size > board.width) {
				selectedVehicle.x = board.width - selectedVehicle.size;
			} else {
				// then check vehicles
				for(i in board.vehicles) {
					var v = board.vehicles[i];
					// skip selected vehicle
					if(v == i) {
						continue;
					}
					if(v.horiz) {
					} else {
					}
				}
				// move vehicle
				selectedVehicle.x = newX;
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
	// snap selected vehicle to nearest spot
	if(selectedVehicle.horiz) {
		selectedVehicle.x = Math.round(selectedVehicle.x);
	} else {
		selectedVehicle.y = Math.round(selectedVehicle.y);
	}
	// draw frame
	drawFrame();
	// deselect vehicle
	selectedVehicle = null;
});



/* TESTING */
var board = new Board(6, 6, new Exit('E', 2));

board.addVehicle(new Vehicle(false, true, 3, 0, 0));
board.addVehicle(new Vehicle(true, false, 2, 0, 2));

drawFrame();
