var vehicleColor = '#0000FF'
var vipColor = '#FF0000'
var squareSize = 40

function Board(length, width) {
	this.length = length;
	this.width = width;
	this.vehicles = [];
	this.exit = {
		cardinal: null,
		offset: 0
	}
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
		ctx.rect(vehicle.x * squareSize, vehicle.y * squareSize, (vehicle.x + vehicle.length) * squareSize, (vehicle.y + 1) * squareSize);
	} else {
		ctx.rect(vehicle.x * squareSize, vehicle.y * squareSize, (vehicle.x + 1) * squareSize, (vehicle.y + vehicle.length) * squareSize);
	}
	if(vehicle.isVip) {
		ctx.fillStyle = vehicleColor;
	} else {
		ctx.fillStyle = vipColor;
	}
	ctx.fill();
	ctx.closePath();
}

var canvas = document.getElementById("gameCanvas");
var ctx = canvas.getContext("2d");

var v = new Vehicle(false, true, 3, 0, 0);
drawVehicle(v);

