var ehriControllers = angular.module('ehri-controller', []);

var examples = [
    "Contains correspondence with, and notes about, the following former prisoners re songs from various prisons: Charewicz, Czarnecka, Kurkiewiczowa, Urbanska, Wanat, Zablocka-Racina, Rodowod, Domanski, Bartkowiak, Ligeza, Godlewski, and Broda first names not given. Also contains information about prison songs from Tarnow, Pawiak, Radom, and Wronki prisons in Poland.",
    "Selected materials related to concentration camps Bełżec, Treblinka, Chełmno, Majdanek, Auschwitz-Birkenau, Płaszòw, and Gross-Rosen; ghettos in Warsaw, Siedlce, and Limanowa; and the labor camps for Jews in Poznań: testimony of witnesses and suspects, photographs, postcards, letters, certificates of death, travel passes, texts of prayers, staff lists, lists of ex-prisoners, documents of Poland’s military mission in London, daily reports of the Leiter des Ordnungsdienstes (Head of Order Service) of the Warsaw ghetto."
];

ehriControllers.controller('textProcessingController', function ($scope, $http) {
    
    $scope.example  = function(n) {
        $scope.text = examples[n];
    };

    $scope.showMap = function () {
        var width = 1000, height = 500;

        $scope.projection = d3.geo.mercator()
            .center([0, 40])
            .scale(400)
            .rotate([0, 0]);

        var chartRoot = d3.select("#map-chart");
        var svg = chartRoot.select("svg");
        if (!svg.empty()) {
            svg.remove();
        }
        svg = chartRoot.append("svg")
            .attr("width", width)
            .attr("height", height);

        var path = d3.geo.path()
            .projection($scope.projection);

        var g = svg.append("g");

        // load and display the World
        d3.json("https://s3-us-west-2.amazonaws.com/vida-public/geo/world-topo-min.json", function (error, topology) {
            g.selectAll("path")
                .data(topojson.object(topology, topology.objects.countries)
                    .geometries)
                .enter()
                .append("path")
                .attr("d", path);

            g.selectAll("circle")
                .data($scope.results)
                .enter()
                .append("a")
                .attr("xlink:href", function (d) {
                        return "https://www.google.com/search?q=" + d.name;
                    }
                )
                .append("circle")
                .attr("cx", function (d) {
                    return $scope.projection([d.coordinates.longitude, d.coordinates.latitude])[0];
                })
                .attr("cy", function (d) {
                    return $scope.projection([d.coordinates.longitude, d.coordinates.latitude])[1];
                })
                .attr("r", 5)
                .style("fill", "red");

            g.selectAll("text")
                .data($scope.results)
                .enter()
                .append("text") // append text
                .attr("x", function (d) {
                    return $scope.projection([d.coordinates.longitude, d.coordinates.latitude])[0];
                })
                .attr("y", function (d) {
                    return $scope.projection([d.coordinates.longitude, d.coordinates.latitude])[1];
                })
                .attr("dy", -7) // set y position of bottom of text
                .style("fill", "black") // fill the text with the colour black
                .attr("text-anchor", "middle") // set anchor y justification
                .text(function (d) {
                    return d.name;
                });
        });


        // zoom and pan
        var zoom = d3.behavior.zoom()
            .on("zoom", function () {
                g.attr("transform", "translate(" +
                    d3.event.translate.join(",") + ")scale(" + d3.event.scale + ")");
                g.selectAll("circle")
                    .attr("d", path.projection($scope.projection));
                g.selectAll("path")
                    .attr("d", path.projection($scope.projection));
            });

        svg.call(zoom)
    };

    /*$scope.showLocations = function () {

     if (!$scope.results) {
     return;
     }

     var g = d3.select("svg").select("g");
     var path = g.select("something");

     console.log(path);
     path.selectAll("circle")
     .data($scope.results)
     .enter()
     .append("a")
     .attr("xlink:href", function (d) {
     return "https://www.google.com/search?q=" + d.name;
     }
     )
     .append("circle")
     .attr("cx", function (d) {
     return $scope.projection([d.coordinates.longitude, d.coordinates.latitude])[0];
     })
     .attr("cy", function (d) {
     return $scope.projection([d.coordinates.longitude, d.coordinates.latitude])[1];
     })
     .attr("r", 5)
     .style("fill", "red");

     path.parent().selectAll("text")
     .data($scope.results)
     .enter()
     .append("text") // append text
     .attr("x", function (d) {
     return $scope.projection([d.coordinates.longitude, d.coordinates.latitude])[0];
     })
     .attr("y", function (d) {
     return $scope.projection([d.coordinates.longitude, d.coordinates.latitude])[1];
     })
     .attr("dy", -7) // set y position of bottom of text
     .style("fill", "black") // fill the text with the colour black
     .attr("text-anchor", "middle") // set anchor y justification
     .text(function (d) {
     return d.name;
     });


     };*/

    $scope.process = function (text) {

        var textToBeSent = {
            text: text
        };

        $http(
            {
                method: 'POST',
                url: '/geotagNerdLocations',
                data: textToBeSent
            }
        ).then(
            function success(response) {
                console.log(response.data)
                console.log(response.data.OK);
                if (response.data.OK) {
                    $scope.results = response.data.locations;

                    $scope.showMap();
                }
            },
            function failure(error) {
                $scope.results = error;
            }
        )
    }

});

ehriControllers.controller('mapChart', function ($scope) {

});