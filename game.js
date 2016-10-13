function Board(length, width) {
	this.length = length;
	this.width = width;
	this.vehicles = [];
	this.vip = null;
	this.exit = {
		cardinal: null;
		offset: 0;
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

var canvas = document.getElementById("myCanvas");
var ctx = canvas.getContext("2d");

ctx.beginPath();

// game goes here

ctx.closePath();
