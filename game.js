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
			draw();
			
		}
	};
	reader.readAsText(file);
}
document.getElementById('files').addEventListener('change', handleFileSelect, false);

function drawVehicle(vehicle) {
	ctx.beginPath();
	if(vehicle.horiz) {
		ctx.rect(vehicle.x * squareSize + 1, vehicle.y * squareSize + 1, vehicle.length * squareSize - 2, squareSize - 2);
	} else {
		ctx.rect(vehicle.x * squareSize + 1, vehicle.y * squareSize + 1, squareSize - 2, vehicle.length * squareSize - 2);
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

function testFunction() {
	var x = document.getElementById("myFile");
	x.disabled = true;
	importBoard(x.file);
}

var canvas = document.getElementById("gameCanvas");
var ctx = canvas.getContext("2d");
