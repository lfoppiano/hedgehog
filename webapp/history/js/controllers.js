var app = angular.module('date-application', ['ngSanitize', 'ui.bootstrap']);

var examples = [
    "L'extrême-gauche de la Résistance affiche un scepticisme critique. Je vois Yves qui m'avait cité l'impatience d'Alger devant le cas Pucheu comme une illustration de la crise du Gaullisme.",
    "Photo Album of Boy Scouts Summer Camp created by Jewish refugee in Shanghai, China: orange silk cover with dragon pattern; pages tied together with orange yarn; handwritten captions written in silver ink; 150 photographs attached to pages; inscription in silver ink written handwritten inside front cover: “This book will tell a story - a story of a camp - the SUMMER CAMP of the 13th Shanghai (United) Group, held at Holt’s wharf - Pootung - from August 17th to 31st, with the kind permission and help of the Wharf officials. If I or any member of the group, who took part at this camp, shall look over this book of pictures in future days, we shall remember - what was considered at the end of camp - the nicest adventure we had so far. It was a hard week for me and my assistants - the Scouts and Rovers of our group - but when we were assured by every participant that they all enjoyed it tremendously much, we realized that our work was not done in vain, but for the interest of youth and for the everlasting ideals of scouting.”",
    "The Gulf War (2 August 1990 – 28 February 1991), codenamed Operation Desert Shield (2 August 1990 – 17 January 1991) for operations leading to the buildup of troops and defence of Saudi Arabia and Operation Desert Storm (17 January 1991 – 28 February 1991) in its combat phase, was a war waged by coalition forces from 35 nations led by the United States against Iraq in response to Iraq's invasion and annexation of Kuwait.\n The initial conflict to expel Iraqi troops from Kuwait began with an aerial and naval bombardment on 17 January 1991, continuing for five weeks. This was followed by a ground assault on 24 February. This was a decisive victory for the coalition forces, who liberated Kuwait and advanced into Iraqi territory. The coalition ceased its advance, and declared a ceasefire 100 hours after the ground campaign started. Aerial and ground combat was confined to Iraq, Kuwait, and areas on Saudi Arabia's border. Iraq launched Scud missiles against coalition military targets in Saudi Arabia and against Israel."
];

app.controller('nerdController', function ($scope, $http, $sce) {

    $scope.fetchExample = function (n) {
        $scope.text = examples[n];
    };

    $scope.showResults = function (text, data) {
        annotatedText = text;

        entitiesList = data['entities'];
        var lastMaxIndex = text.length;

        var currentAnnotationIndex = entitiesList.length - 1;

        for (var entityIndex = entitiesList.length - 1; entityIndex >= 0; entityIndex--) {
            var entity = entitiesList[entityIndex];

            var startEntity = parseInt(entity.offsetStart, 10);
            var endEntity = parseInt(entity.offsetEnd, 10);

            var startHead = parseInt(entity.head.offsetStart, 10);
            var endHead = parseInt(entity.head.offsetEnd, 10);

            if (startEntity > lastMaxIndex) {
                // we have a problem in the initial sort of the entities
                // the server response is not compatible with the client
                console.log("Sorting of entities as present in the server's response not valid for this client.");
            } else if (endEntity > lastMaxIndex) {
                endEntity = lastMaxIndex;
                lastMaxIndex = startEntity;
            } else {
                if (startEntity < startHead) {
                    annotatedText = annotatedText.substring(0, startEntity)
                        + '<span id="annot-' + entityIndex + '" class="label ' + 'entity' + '" style="cursor:hand;cursor:pointer;">'
                        + annotatedText.substring(startEntity, endEntity)
                        + '</span>'
                        + annotatedText.substring(endEntity, startHead)
                        + '<span id="annot-' + entityIndex + '" class="label ' + 'head' + '" style="cursor:hand;cursor:pointer;">'
                        + annotatedText.substring(startHead, endHead)
                        + '</span>'
                        + annotatedText.substring(endHead, annotatedText.length + 1);
                    lastMaxIndex = startEntity

                } else {
                    annotatedText = annotatedText.substring(0, startHead)
                        + '<span id="annot-' + entityIndex + '" class="label ' + 'head' + '" style="cursor:hand;cursor:pointer;">'
                        + annotatedText.substring(startHead, endHead)
                        + '</span>'
                        + annotatedText.substring(endHead, startEntity)
                        + '<span id="annot-' + entityIndex + '" class="label ' + 'entity' + '" style="cursor:hand;cursor:pointer;">'
                        + annotatedText.substring(startEntity, endEntity)
                        + '</span>'
                        + annotatedText.substring(endEntity, annotatedText.length + 1);
                    lastMaxIndex = startHead;
                }
                console.log(annotatedText);
                currentAnnotationIndex = entityIndex;
            }
        }

        $scope.result = $sce.trustAsHtml(annotatedText);
    };

    $scope.process = function (text) {
        var textToBeSent = text;

        $http(
            {
                method: 'POST',
                url: '/processHistory',
                data: {"text": textToBeSent}
            }
        ).then(
            function success(response) {
                if (response.status == 200) {
                    $scope.showResults(text, response.data);
                }
            },
            function failure(error) {
                $scope.results = error;
            }
        );
    }

});