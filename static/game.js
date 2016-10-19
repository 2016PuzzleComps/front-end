var puzzleServerURL = 'localhost'
 
var vehicleColor = '#306aad';
var vipColor = '#b54141';
var squareSize = 100;
var board;
var initialBoard = "";

function Board(width, height, exit_offset) {
	this.width = width;
	this.height = height;
	this.vehicles = [];
	this.exit_offset = exit_offset;
	// create 2d array of false
	this.occupied = [];
	for(var x = 0; x < this.width; x++) {
		this.occupied[x] = [];
		for(var y = 0; y < this.height; y++) {
			this.occupied[x][y] = false;
		}
	}
	// borders
	this.occupied[-1] = [];
	this.occupied[this.width] = [];
	for(var x = 0; x < this.width; x++) {
		this.occupied[x][-1] = true;
		this.occupied[x][this.height] = true;
	}
	for(var y = 0; y < this.height; y++) {
		this.occupied[-1][y] = true;
		this.occupied[this.width][y] = true;
	}
	// exit
	this.occupied[this.width][this.exit_offset] = false;
	var i = 1;
	for(; i <= 1; i++) { // for now just assume the vip car has size 2
		this.occupied[this.width+i] = [];
		this.occupied[this.width+i][this.exit_offset] = false;
	}
	this.occupied[this.width+i] = [];
	this.occupied[this.width+i][this.exit_offset] = true;
}

Board.prototype.addVehicle = function(v) {
	this.vehicles.push(v);
	this.placeVehicle(v, true);
}

Board.prototype.placeVehicle = function(v, down) {
	if(v.horiz) {
		for(var i = 0; i < v.size; i++) {
			this.occupied[v.x + i][v.y] = down;
		}
	} else {
		for(var i = 0; i < v.size; i++) {
			this.occupied[v.x][v.y + i] = down;
		}
	}
}

function Vehicle(isVip, horiz, size, x, y) {
	this.isVip = isVip;
	this.horiz = horiz;
	this.size = size;
	this.x = x;
	this.y = y;
}

// Handles a user uploading a file
function handleFileSelect(evt) {
	var files = evt.target.files; // FileList object

	// files is a FileList of File objects. List some properties.
	var output = [];
	var file = files[0];
	var reader = new FileReader();

	// If we use onloadend, we need to check the readyState.
	reader.onloadend = function(evt) {
		if (evt.target.readyState == FileReader.DONE) { // DONE == 2
			loadBoardFromText(evt.target.result);
		}
	};
	reader.readAsText(file);
}

// Loads a board from a given block of text
function loadBoardFromText(text) {
	initialBoard = text;
	var lines = text.split("\n");
	var dimen = lines[0].split(" ");
	var exitOffset = parseInt(lines[1]);
	board = new Board(parseInt(dimen[0]), parseInt(dimen[1]), exitOffset);
	var isFirst = true;
	for (var i=2; i<lines.length; i++) {
		var items = lines[i].split(" ");
		if (items.length != 4) {
			break;
		}
		var newVehicle = new Vehicle(isFirst, items[3].charAt(0)=="T", parseInt(items[2]), parseInt(items[0]), parseInt(items[1]));
		board.addVehicle(newVehicle);
		if (isFirst) {
			isFirst = false;
		}
	}
	drawFrame();
}

// Resets the board to the initial state (if there is one)
function resetBoard() {
	if (initialBoard != "") {
		loadBoardFromText(initialBoard);
	}
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
	context.stroke();
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
	var clearX, clearY;
	var clearWidth = squareSize - 2;
	var clearHeight = squareSize - 2;
	clearX = (board.width * squareSize) - 1;
	clearY = board.exit_offset * squareSize + 1;
	context.clearRect(clearX, clearY, clearWidth, clearHeight);
	// draw vehicles
	for(i in board.vehicles) {
		drawVehicle(board.vehicles[i]);
	}
}

var canvas = document.getElementById("gameCanvas");
var context = canvas.getContext("2d");

/* MOUSE/TOUCH EVENTS */

var fingerDown = false;

// index of vehicle in board.vehicles that is selected by mouse
var selectedVehicleIndex = null;
// offset from origin of selected vehicle
var mouseOffset = 0;
// previous position of selected vehicle
var prevPos = {
	x: 0,
	y: 0
}

// get position of mouse at a mouse event
function getMousePos(evt) {
	var rect = canvas.getBoundingClientRect();
	return {
		x: evt.clientX - rect.left,
		y: evt.clientY - rect.top
	};
}

// get position of finger at a touch event
function getTouchPos(evt) {
	var rect = canvas.getBoundingClientRect();
	return {
		x: evt.touches[0].clientX - rect.left,
		y: evt.touches[0].clientY - rect.top
	};
}

// select vehicle
canvas.addEventListener('mousedown', function(evt) {
	selectVehicle(getMousePos(evt));
});
canvas.addEventListener('touchstart', function(evt) {
	if(evt.changedTouches[0].identifier == 0) {
		selectVehicle(getTouchPos(evt));
	}
	fingerDown = true;
});

// deselect vehicle
canvas.addEventListener('mouseup', deselectVehicle);
canvas.addEventListener('mouseleave', deselectVehicle);
canvas.addEventListener('touchleave', deselectVehicle);
canvas.addEventListener('touchend', function(evt) {
	if(evt.changedTouches[0].identifier == 0) {
		deselectVehicle();
		fingerDown = false;
	}
});

// move vehicle
canvas.addEventListener('mousemove', function(evt) {
	if(!fingerDown) {
		moveVehicle(getMousePos(evt));
	}
});
canvas.addEventListener('touchmove', function(evt) {
	if(evt.changedTouches[0].identifier == 0) {
		moveVehicle(getTouchPos(evt));
	}
});

function selectVehicle(pos) {
	// if puzzle is loaded
	if(!board) {
		return;
	}
	// find if pos is over a vehicle on the board
	for(i in board.vehicles) {
		var v = board.vehicles[i];
		if(v.horiz) {
			if((v.x * squareSize <= pos.x) && (pos.x <= (v.x + v.size) * squareSize) && (v.y * squareSize <= pos.y) && (pos.y <= (v.y + 1) * squareSize)) {
				selectedVehicleIndex = i;
				mouseOffset = pos.x - (v.x * squareSize);
				break;
			}
		} else {
			if((v.x * squareSize <= pos.x) && (pos.x <= (v.x + 1) * squareSize) && (v.y * squareSize <= pos.y) && (pos.y <= (v.y + v.size) * squareSize)) {
				selectedVehicleIndex = i;
				mouseOffset = pos.y - (v.y * squareSize);
				break;
			}
		}
	}
	if(selectedVehicleIndex != null) {
		var selectedVehicle = board.vehicles[selectedVehicleIndex];
		prevPos.x = selectedVehicle.x;
		prevPos.y = selectedVehicle.y;
		board.placeVehicle(selectedVehicle, false);
	}
}

function moveVehicle(pos) {
	if(selectedVehicleIndex != null) {
		var selectedVehicle = board.vehicles[selectedVehicleIndex];
		if(selectedVehicle.horiz) {
			var newX = (pos.x - mouseOffset) / squareSize;
			// check other vehicles
			if(newX < selectedVehicle.x) {
				// if it's being dragged to the left
				var testX = Math.floor(selectedVehicle.x) - 1;
				if(newX - 1 <= testX && board.occupied[testX][selectedVehicle.y]) {
					newX = testX + 1;
				}
			} else {
				// if it's being dragged to the right
				var testX = Math.ceil(selectedVehicle.x) + selectedVehicle.size;
				if(newX + selectedVehicle.size >= testX && board.occupied[testX][selectedVehicle.y]) {
					newX = testX - selectedVehicle.size;
				}
			}
			// move vehicle horizontally
			selectedVehicle.x = newX;
		} else {
			var newY = (pos.y - mouseOffset) / squareSize;
			// check other vehicles
			if(newY < selectedVehicle.y) {
				// if it's being dragged up
				// see if next square up is occupied
				var testY = Math.floor(selectedVehicle.y) - 1;
				if(newY - 1 <= testY && board.occupied[selectedVehicle.x][testY]) {
					newY = testY + 1;
				}
			} else {
				// if it's being dragged down
				// see if next square down is occupied
				var testY = Math.ceil(selectedVehicle.y) + selectedVehicle.size;
				if(newY + selectedVehicle.size >= testY && board.occupied[selectedVehicle.x][testY]) {
					newY = testY - selectedVehicle.size;
				}
			}
			// move vehicle vertically
			selectedVehicle.y = newY;
		}
		drawFrame();
	}
}

function deselectVehicle(evt) {
	if(selectedVehicleIndex) {
		var selectedVehicle = board.vehicles[selectedVehicleIndex];
		// snap selected vehicle to nearest spot
		if(selectedVehicle.horiz) {
			selectedVehicle.x = Math.round(selectedVehicle.x);
		} else {
			selectedVehicle.y = Math.round(selectedVehicle.y);
		}
		board.placeVehicle(selectedVehicle, true);
		// draw frame
		drawFrame();
		drawFrame();
		// check for victory and output code
		if(selectedVehicle.isVip && selectedVehicle.x >= board.width) {
			var code = generateCode();
			document.getElementById("code").innerHTML = "Puzzle Code: " + code;
			alert("You've won! ");
		}
		// deselect vehicle
		selectedVehicleIndex = null;
	}
}

// Generates a code that the worker will user to recieve payment on MTurk
function generateCode() {
	return 34;
}

// prevent touch scrolling
document.body.addEventListener("touchstart", function (e) {
	if (e.target == canvas) {
		e.preventDefault();
	}
}, false);
document.body.addEventListener("touchend", function (e) {
	if (e.target == canvas) {
		e.preventDefault();
	}
}, false);
document.body.addEventListener("touchmove", function (e) {
	if (e.target == canvas) {
		e.preventDefault();
	}
}, false);

document.getElementById('files').addEventListener('change', handleFileSelect, false);
document.getElementById('resetButton').onclick = resetBoard;

// LOAD A PUZZLE!
var requester = new XMLHttpRequest();
requester.addEventListener('load', function() {
	loadBoardFromText(this.responseText);
});
requester.open("GET", "http://" + puzzleServerURL + "/puzzle-file");
requester.send();
