/* GLOBAL VARS */

var vehicleColor = '#306aad';
var vipColor = '#b54141';
var squareSize = 100;
var borderWidth = 30;
var borderColor = '#916f25';
var boardColor = '#e8d39b';

var board;
var initialBoard = "";
var moveListLog = [];
var currentMoveNum = 0;
var resetBoards = [];
var currentTimeout;

var pause = false;
var totalMoves;

/*
var buttonAdded = false;
function insertQuitButton() {
	var giveUpButton = document.createElement("giveUpButton");
	var text = document.createTextNode("Give Up");
	giveUpButton.appendChild(text);
	giveUpButton.className = "button";
	giveUpButton.classList.add("giveUpButton");
	buttonDiv = document.getElementById("buttonsDiv");
	buttonDiv.appendChild(giveUpButton);
	giveUpButton.onclick = giveUp;
	buttonAdded = true;
}*/

/* Puzzle and log file uploading */

// receive puzzle from server
function handlePuzzleUpload(evt) {
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

    document.getElementById('log_file').disabled=false;
}

// receive puzzle from server
function handleLogUpload(evt) {
    var files = evt.target.files; // FileList object

	// files is a FileList of File objects. List some properties.
	var output = [];
	var file = files[0];
	var reader = new FileReader();

	// If we use onloadend, we need to check the readyState.
	reader.onloadend = function(evt) {
		if (evt.target.readyState == FileReader.DONE) { // DONE == 2
			parseLogFile(evt.target.result);
		}
	};
	reader.readAsText(file);
}


/* FILE PARSERS */

function parseLogFile(text) {
	var lines = text.split("\n");
	totalMoves = 0;
	for (var i=0; i<lines.length; i++) {
		var items = lines[i].split(" ");
		// If there is an error, display a message
		if (items.length < 2 || items.length > 3) {
			alert("Error in log file");
			return;
		} 
		var time = parseInt(items[0]);
		// Handle undo and reset separately 
		if (items.length == 2) {
			var type = items[1].trim();
			if (type === 'U' && totalMoves > 0) {
				// Store the undo move as a regular move, only backwards
				var lastMove = moveListLog[totalMoves-1];
				moveListLog.push(new LogMove(lastMove.vehicle, lastMove.fpos, lastMove.ipos, time, type));
			} else if (type === 'R' && totalMoves > 0) {
				moveListLog.push(new LogMove(null, null, null, time, type));
			} else {
				alert("Error in log file");
				return;
			}
		} else if (items.length == 3) {
			var currentVehicle = board.vehicles[parseInt(items[1])];
			var dist = parseInt(items[2]);
			if (currentVehicle.horiz) {
				moveListLog.push(new LogMove(currentVehicle,currentVehicle.x, currentVehicle.x + dist, time, 'N'));
			} else {
				moveListLog.push(new LogMove(currentVehicle, currentVehicle.y, currentVehicle.y + dist, time, 'N'));
			}
		} else {
			alert("Error in log file");
			return;
		}
		doLogMove(moveListLog[totalMoves]);
		totalMoves += 1;
	}
	for (var j=totalMoves-1; j>=0; j--) {
		undoLogMove(moveListLog[j]);
	}
	playMoves();
}

/* MOVEMENT FUNCTIONS */

function handleBack() {
	if (!pause) {
		togglePlay();
	} moveBack();
}

function handleForward() {
	if (!pause) {
		togglePlay();
	} moveForward();
}

// Moves back one move in the log
function moveBack() {
	if (currentMoveNum > 0 && currentMoveNum <= totalMoves) {
		var move = moveListLog[currentMoveNum - 1];
		undoLogMove(move);
		currentMoveNum -= 1;
		drawFrame();
	}
}

// Moves forward one move in the log
function moveForward() {
	if (currentMoveNum < totalMoves) {
		var move = moveListLog[currentMoveNum];
		doLogMove(move);
		currentMoveNum += 1;
		drawFrame();
	} else {
		pause = true;
	}
}

// Undoes a particular move
function undoLogMove(lastMove) {
	var currentPos;
	
	if (lastMove.type === 'R') {
		undoLogReset();
		return;
	}
	// remove the vehicle from the prototype
	board.placeVehicle(lastMove.vehicle, false);
	if (lastMove.vehicle.horiz) {
		currentPos = lastMove.vehicle.x;
	} else {
		currentPos = lastMove.vehicle.y;
	}
	moveVehicleTo(lastMove.vehicle, currentPos + (lastMove.ipos - lastMove.fpos));
}

// Does a particular move
function doLogMove(nextMove) {
	var currentPos;

	if (nextMove.type === 'R') {
		doLogReset();
		return;
	}
	// remove the vehicle from the prototype
	board.placeVehicle(nextMove.vehicle, false);
	if (nextMove.vehicle.horiz) {
		currentPos = nextMove.vehicle.x;
	} else {
		currentPos = nextMove.vehicle.y;
	}
	moveVehicleTo(nextMove.vehicle, currentPos + (nextMove.fpos - nextMove.ipos));
}

// Undoes a reset that was in the log
function undoLogReset() {
	resetBoardToText(resetBoards.pop());
}

// Does a basic reset, but saves the positions of the cars
function doLogReset() {
	var text = saveBoardToText();
	resetBoards.push(text);
	resetBoardToText(initialBoard);
}

// moves a vehicle to the given position
function moveVehicleTo(vehicle, pos) {
	if (vehicle.horiz) {
		vehicle.x = pos;
	} else {
		vehicle.y = pos;
	}
	// place the vehicle in the prototype
	board.placeVehicle(vehicle, true);
	drawFrame();
}

/* CLASS DEFINITION STUFF */

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

function Move(vehicle, ipos, fpos) {
	this.vehicle = vehicle;
	this.ipos = ipos;
	this.fpos = fpos;
}

function LogMove(vehicle, ipos, fpos, time, type) {
	this.vehicle = vehicle;
	this.ipos = ipos;
	this.fpos = fpos;
	this.time = time;
	// Type is normal, undo, or reset: 'N', 'U', 'R'
	this.type = type;
}

/* CANVAS STUFF */

var canvas = document.getElementById("gameCanvas");
var context = canvas.getContext("2d");

// draw a vehicle to the canvas
function drawVehicle(vehicle) {
	context.beginPath();
	if(vehicle.isVip) {
		context.fillStyle = vipColor;
	} else {
		context.fillStyle = vehicleColor;
	}
	if(vehicle.horiz) {
		context.rect((vehicle.x * squareSize) + borderWidth, (vehicle.y * squareSize) + borderWidth, vehicle.size * squareSize, squareSize);
	} else {
		context.rect((vehicle.x * squareSize) + borderWidth, (vehicle.y * squareSize) + borderWidth, squareSize, vehicle.size * squareSize);
	}
	context.fill();
	context.stroke();
}

// render a frame
function drawFrame() {
	// clear everything //
	context.clearRect(0, 0, canvas.width, canvas.height);
	// draw border //
	// brown border
	context.fillStyle = borderColor;
	context.fillRect(0, 0, (borderWidth * 2) + (board.width * squareSize), (borderWidth * 2) + (board.height * squareSize));
	// light brown inside
	context.fillStyle = boardColor;
	context.fillRect(borderWidth, borderWidth, board.width * squareSize + 2, board.height * squareSize);
	// exit is part of board //
	var clearX, clearY;
	var clearWidth = borderWidth + 1;
	var clearHeight = squareSize;
	clearX = borderWidth + (board.width * squareSize) - 1;
	clearY = borderWidth + (board.exit_offset * squareSize);
	context.fillRect(clearX, clearY, clearWidth, clearHeight);
	// draw lines around board
	context.beginPath();
	context.moveTo(0,0);
	context.lineTo(borderWidth * 2 + (board.width * squareSize), 0);
	context.lineTo(borderWidth * 2 + (board.width * squareSize), clearY);
	context.lineTo(clearX + 2, clearY);
	context.lineTo(clearX + 2, borderWidth);
	context.lineTo(borderWidth, borderWidth);
	context.lineTo(borderWidth, borderWidth + (board.height * squareSize));
	context.lineTo(clearX + 2, borderWidth + (board.height * squareSize));
	context.lineTo(clearX + 2, clearY + clearHeight);
	context.lineTo(clearX + clearWidth, clearY + clearHeight);
	context.lineTo(clearX + clearWidth, (board.height * squareSize) + (borderWidth * 2));
	context.lineTo(0, (board.height * squareSize) + (borderWidth * 2));
	context.closePath();
	context.stroke();
	// draw vehicles //
	for(i in board.vehicles) {
		drawVehicle(board.vehicles[i]);
	}
}

function togglePlay() {
	if (pause) {
		pause = false;
		playNextMove();
		document.getElementById('playPause').innerHTML = 'pause';
	} else {
		pause = true;
		clearTimeout(currentTimeout);
		document.getElementById('playPause').innerHTML = 'play_arrow';
	}
}

// Starts playing the moves as they occurred in the log file
function playMoves() {
	if (currentMoveNum != 0) {
		return;
	}
	playNextMove();
}

// Plays the next move
function playNextMove() {
	// If we're at the end, stop scheduling more moves
	if (currentMoveNum >= totalMoves) { return; }

	// Get the starting time for the timeout
	var start = moveListLog[0].time - 250;
	if (currentMoveNum > 0) {
		start = moveListLog[currentMoveNum-1].time;
	}
	currentTimeout = setTimeout(function() {
		moveForward();
		playNextMove();
	}, moveListLog[currentMoveNum].time-start);
}

/* BOARD <-> TEXT FUNCTIONS */

// Loads a board from a given block of text
function loadBoardFromText(text) {
	var lines = text.split("\n");
	var dimen = lines[0].split(" ");
	// Do some validation on the log file
	if (lines.length < 2) {
		alert("Incorrect puzzle file format, it is too short");
		document.getElementById('log_file').disabled=false;
		return;
	} if (dimen.length != 2) {
		alert("Incorrect puzzle file format on line 1");    
		document.getElementById('log_file').disabled=false;
		return;
	}
	initialBoard = text;
	var exitOffset = parseInt(lines[1].split(" ")[1]);
	board = new Board(parseInt(dimen[0]), parseInt(dimen[1]), exitOffset);
	var isFirst = true;
	for (var i=1; i<lines.length; i++) {
		var items = lines[i].split(" ");
		if (items.length != 4) {
			if (items.length < 2) { break; }
			alert("Incorrect puzzle file format on line "+(i+1));
			document.getElementById('log_file').disabled=false;
			return;
		}
		var newVehicle = new Vehicle(isFirst, items[3].charAt(0)=="T", parseInt(items[2]), parseInt(items[0]), parseInt(items[1]));
		board.addVehicle(newVehicle);
		if (isFirst) {
			isFirst = false;
		}
	}
	drawFrame();
}

// Resets a board to the board described in a block of text
function resetBoardToText(text) {
	var lines = text.split("\n");
	for (var i=1; i<lines.length; i++) {
		var curVehicle = board.vehicles[i-1];
		var items = lines[i].split(" ");
		if (items.length != 4) {
			break;
		}

		board.placeVehicle(curVehicle, false);

		curVehicle.x = parseInt(items[0]);
		curVehicle.y = parseInt(items[1]);

		board.placeVehicle(curVehicle, true);
	}
	drawFrame();
}

function saveBoardToText() {
	var text=board.width + " " + board.height + " " + "\n";
	for (var i in board.vehicles) {
		var curVehicle = board.vehicles[i];
		var isHoriz = "T";
		if (!curVehicle.horiz) { isHoriz = "F"; }
		text += curVehicle.x + " " + curVehicle.y + " " + curVehicle.size + " " + isHoriz + "\n";
	}
	return text;
}

// Set the button actions
document.getElementById('backButton').onclick = handleBack;
document.getElementById('forwardButton').onclick = handleForward;
document.getElementById('playPause').onclick = togglePlay;


document.getElementById('puzzle_file').addEventListener('change', handlePuzzleUpload, false);
document.getElementById('log_file').addEventListener('change', handleLogUpload, false);