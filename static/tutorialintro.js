function startIntro() {
    var intro = introJs();
    intro.setOptions({
        steps: [{
            intro: "Welcome to the tutorial. Here you'll learn how to play the game."
        },{
            intro: "The goal is to move the red block out of the box."
        },{
            element: '#gameCanvas',
            intro: "You can interact with the blocks here with mouse or touch (if on a compatible device). Each car can only move in the direction of its long sides.",
            position: 'right'
        },{
            element: '#resetButton',
            intro: 'If you get stuck, you can click here to reset to the inital state.',
            position: 'right'
        },{
            element: '#undoButton',
            intro: 'Or if you want to go back a number of moves, you can undo.',
            position: 'right'
        },{
            element: '#giveupButton',
            intro: 'If you can\'t solve the puzzle, a button will appear and you can give up. You won\'t get a token, but you will be given another puzzle.<br/><a class="button" href="javascript:void(0);" onclick="javascript:insertQuitButton();">Show button</a>',
            position: 'right'
        },{
            intro: 'Feel free to play around with this tutorial. In the real link, your token will appear once the puzzle has been correctly solved (no cheating!)'
        },{
            intro: 'Have fun!'
        }]
    });

    intro.start();
}
