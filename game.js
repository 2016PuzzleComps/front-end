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

function Vehicle(isVip, horiz, length, x, y) {
	this.isVip = isVip;
	this.horiz = horiz;
	this.length = length;
	this.x = x;
	this.y = y;
}

function drawVehicle(vehicle) {
	ctx.beginPath();
	if(vehicle.horiz) {
		ctx.rect(vehicle.x * squareSize, vehicle.y * squareSize, vehicle.length * squareSize, squareSize);
	} else {
		ctx.rect(vehicle.x * squareSize, vehicle.y * squareSize, squareSize, vehicle.length * squareSize);
	}
	if(vehicle.isVip) {
		ctx.fillStyle = vipColor;
	} else {
		ctx.fillStyle = vehicleColor;
	}
	ctx.fill();
	ctx.closePath();
}

function draw() {
	// draw board grid
	for(var i = 0; i <= board.width; i++) {
		ctx.moveTo(0, (i * squareSize));
		ctx.lineTo(board.width * squareSize, (i * squareSize));
		ctx.stroke();
	}
	for(var i = 0; i <= board.height; i++) {
		ctx.moveTo((i * squareSize), 0);
		ctx.lineTo((i * squareSize), board.height * squareSize);
		ctx.stroke();
	}
	// clear exit
	if(board.exit.cardinal == 'E') {
		ctx.clearRect((board.width * squareSize) - 1, (board.exit.offset * squareSize) + 1, squareSize - 2, squareSize - 2);
	}
	// draw vehicles
	for(i in board.vehicles) {
		drawVehicle(board.vehicles[i]);
	}
}

var canvas = document.getElementById("gameCanvas");
var ctx = canvas.getContext("2d");

var board = new Board(6, 6, new Exit('E', 2));

board.addVehicle(new Vehicle(false, true, 3, 0, 0));
board.addVehicle(new Vehicle(true, false, 2, 0, 2));

draw();
