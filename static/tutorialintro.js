function startIntro() {
    var intro = introJs();
    intro.setOptions({
        steps: [{
            intro: "Hello world!"
        },{
            intro: "We can select a number of things"
        },{
            element: '#gameCanvas',
            intro: "This might be a tooltip",
            position: 'right'
        },{
            element: '#resetButton',
            intro: 'Click here to reset to the inital state',
            position: 'right'
        }]
    });

    intro.start();
}
