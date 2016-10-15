function Board(length, width) {
	this.length = length;
	this.width = width;
	this.vehicles = [];
	this.vip = null;
	this.exit = {
		cardinal: null,
		offset: 0
	}
}
Board.prototype.addVehicle = function(v) {
	this.vehicles.push(v);
}

function Vehicle(length, horiz, x, y) {
	this.horiz = horiz;
	this.length = length;
	this.x = x;
	this.y = y;
}
Vehicle.prototype.moveForward = function() {
	if(this.horiz) {
		this.x++;
	} else {
		this.y++;
	}
}
Vehicle.prototype.moveBackward = function() {
	if(this.horiz) {
		this.x--;
	} else {
		this.y--;
	}
}

var canvas = document.getElementById("gameCanvas");
var ctx = canvas.getContext("2d");

ctx.beginPath();

ctx.rect(20,40,50,50);
ctx.fillStyle="#FF0000";
ctx.fill();

ctx.closePath();
