/* <script> */
        chartData1 = [4, 5, 3];
        chartData2 = [3, 3, 1];

function drawBars() {
        require([
            "dojox/charting/Chart", "dojox/charting/plot2d/ClusteredBars",
            "dojox/charting/themes/Claro", "dojox/charting/axis2d/Default",
            "dojo/domReady!"], 
          function(Chart, Bars, theme) {
              var chart = new Chart("chartNode");
              chart.setTheme(theme);
              chart.addPlot("default", {
                      type: Bars,
                      gap: 5,
                      maxBarSize: 20,
                      labels: true, labelStyle: "outside", labelOffset: -10});
              chart.addAxis("x", {
                      vertical: true, minorTicks: false,
                      labels: [{value: 1, text: 'Beharrlichkeit'},
                               {value: 2, text: 'Belastbarkeit'},
                               {value: 3, text: 'Einsatzbereitschaft'}]});
              chart.addAxis("y", {fixLower: "major", fixUpper: "major", min: 0,
                                  minorTicks: false});
              chart.addSeries("test 1", chartData1, {
                      stroke: {color: "blue", width: 2}, fill: "lightblue"});
              chart.addSeries("test 2", chartData2, {
                      stroke: {color: "red", width: 2}, fill: "#ffaaaa"});
              chart.render();
        });
}
/* </script> */
