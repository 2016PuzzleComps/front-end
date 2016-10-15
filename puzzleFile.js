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
				board.addVehicle(newVehicle);
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


