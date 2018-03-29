var app = angular.module('date-application', ['ngSanitize', 'ui.bootstrap']);

var examples = [
    "L'extrême-gauche de la Résistance affiche un scepticisme critique. Je vois Yves qui m'avait cité l'impatience d'Alger devant le cas Pucheu comme une illustration de la crise du Gaullisme.",
    "J'ai aperçu mon plombier — il y a une véritable joie à retrouver des relations d'autrefois, après quatre années de coupure et de se sentir à l'unisson sur Pétain. Quand il m'en a parlé j'ai hésité à répondre catégoriquement, pour ne pas les choquer et j'ai dit : c'est un pauvre homme. Quel déchaînement : elle m'a dit c'est ainsi que vous appelez un homme qui nuit à son pays, etc... etc... Cette femme, très simple, est vraiment épatante. Elle m'explique que depuis le début elle écoute les informations de la radio anglaise et les diffuse dans le quartier.",
    "Nous parlons d'autres voisins du quartiers que sont-ils devenus. Celui—là vous savez c'est un français... et ça veut tout dire. Elle a raison cela veut tout dire — la droite a éclaté au feu de la guerre — il y a d'un côté les Français, plombiers ou hommes de lettres, et de l'autre ceux qui pensent à leurs gros sous..."
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

            if (entity.head) {
                var startHead = parseInt(entity.head.offsetStart, 10);
                var endHead = parseInt(entity.head.offsetEnd, 10);
            }

            if (startEntity > lastMaxIndex) {
                // we have a problem in the initial sort of the entities
                // the server response is not compatible with the client
                console.log("Sorting of entities as present in the server's response not valid for this client.");
            } else if (endEntity > lastMaxIndex) {
                endEntity = lastMaxIndex;
                lastMaxIndex = startEntity;
            } else {
                if(startHead) {
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
                    currentAnnotationIndex = entityIndex;
                } else {
                    annotatedText = annotatedText.substring(0, startEntity)
                        + '<span id="annot-' + entityIndex + '" class="label ' + 'entity' + '" style="cursor:hand;cursor:pointer;">'
                        + annotatedText.substring(startEntity, endEntity)
                        + '</span>'
                        + annotatedText.substring(endEntity, annotatedText.length + 1);
                    lastMaxIndex = startEntity;
                    currentAnnotationIndex = entityIndex;
                }
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
                    $scope.json = response.data;
                    console.log(response.data)
                } else {
                    $scope.results = response.data;
                }
            },
            function failure(error) {
                $scope.results = error;
            }
        );
    }

});