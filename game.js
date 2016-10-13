function Vehicle(length, x, y) {
	this.length = lenght;
	this.x = x;
	this.y = y;
}
Vehicle.prototype.moveForward = function() {
	// TODO
}
Vehicle.prototype.moveBackward = function() {
	// TODO
}

var canvas = document.getElementById("myCanvas");
var ctx = canvas.getContext("2d");

ctx.beginPath();

// game goes here

ctx.closePath();
