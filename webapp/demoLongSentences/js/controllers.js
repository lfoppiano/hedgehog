var app = angular.module('date-application', ['ngSanitize', 'ui.bootstrap']);

var examples = [
    "\u00c9l\u00e9ment d\u00e9clencheur, ces suicides ont concr\u00e9tis\u00e9 un fond d'inqui\u00e9tudes diffuses li\u00e9es \u00e0 l'\u00e9volution du travail et \u00e0 certaines de ses formes vicieuses qui perturbent l'\u00e9quilibre psychique des travailleurs. Ces actes dramatiques semblaient, en effet, \u00eatre la cons\u00e9quence plus ou moins directe des dangers du travail qu'une s\u00e9rie d'\u00e9tudes d\u00e9non\u00e7ait de longue date et exprimait en termes d'intensification du travail [Gollac et Volkoff 2000] Bu\u00e9, Coutrot et Puech eds. 2004 [Askenazy et al. eds. 2006] et de \u00abmont\u00e9e du stress \u00bb [Buscatto et al. eds. 2008 ; Nasse et L\u00e9geron 2008 ; Loriol 2012]. Les risques li\u00e9s au travail semblaient ainsi \u00e9tendre leur menace \u00e0 de nouvelles dimensions de la sant\u00e9. Sollicit\u00e9, l'\u00c9tat a r\u00e9agi, comme quantit\u00e9 d'autres instances, notamment politiques 4, alimentant la fi\u00e8vre ambiante. \nPour s'en tenir \u00e0 l'\u00c9tat, et, plus pr\u00e9cis\u00e9ment, au Minist\u00e8re du travail, il s'est rapidement dot\u00e9 d'outils susceptibles d'orienter et de hi\u00e9rarchiser son action en constituant, fin 2008, un coll\u00e8ge d'expertise sur le suivi des risques psychosociaux au travail. Cette initiative est l'un des moments cl\u00e9s qui organisent et cristallisent l'inflexion dans la fa\u00e7on de penser la relation entre \u00ab travail \u00bb et \u00ab sant\u00e9 mentale \u00bb, privil\u00e9giant une approche statistique de la question, approche centr\u00e9e sur la mesure des risques plus que sur la compr\u00e9hension des m\u00e9canismes \u00e0 l'\u0153uvre. Ce que la sociologie ou la psychopathologie du travail appr\u00e9hendaient jusqu'alors dans le cadre d'une r\u00e9flexion g\u00e9n\u00e9rale sur le travail et ses \u00e9volutions, notamment techniques, se traite \u00e0 pr\u00e9sent comme un des risques auxquels le travail expose, et dont il importe de mesurer l'\u00e9tendue et non plus de comprendre l'origine. \nLa mati\u00e8re de ce d\u00e9placement r\u00e9side dans les grandes enqu\u00eates nationales sur les conditions de travail r\u00e9alis\u00e9es depuis les ann\u00e9es 1970. Enqu\u00eates sur la base desquelles s'\u00e9tait pr\u00e9cis\u00e9ment \u00e9labor\u00e9e l'hypoth\u00e8se de l'intensification du travail \u00e9voqu\u00e9e plus haut 5. Les conditions de travail y \u00e9taient pr\u00e9sent\u00e9es comme autant de contraintes susceptibles de d\u00e9grader la sant\u00e9 du travailleur : dur\u00e9e, rythme, cycles d'op\u00e9ration, r\u00e9p\u00e9titivit\u00e9 des t\u00e2ches, contr\u00f4le hi\u00e9rarchique, participation aux t\u00e2ches collectives, etc. Un texte ancien d'Alain Cotterreau sur \u00ab l'usure \u00bb ouvri\u00e8re [1983] restitue bien l'esprit qui a pr\u00e9sid\u00e9 \u00e0 l'\u00e9laboration de ces enqu\u00eates par un groupe de statisticiens r\u00e9formateurs qui a r\u00e9ussi \u00e0 les imposer \u00e0 un patronat r\u00e9calcitrant [Gollac et Volkoff 2000]. Il s'agissait, pour eux, de rappeler ce qu'il en co\u00fbte r\u00e9ellement de travailler, contrebalan\u00e7ant ainsi le discours patronal sur les vertus du progr\u00e8s technique qui effaceraient bient\u00f4t toutes les p\u00e9nibilit\u00e9s. Rappeler, en somme, que le travail reste, avant tout, une peine.",
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

            var type = '';

            if ('type' in entity) {
                type = entity.type.toLowerCase();
            }

            var startEntity = parseInt(entity.offsetStart, 10);
            var endEntity = parseInt(entity.offsetEnd, 10);

            if (startEntity > lastMaxIndex) {
                // we have a problem in the initial sort of the entities
                // the server response is not compatible with the client
                console.log("Sorting of entities as present in the server's response not valid for this client.");
            } else if (endEntity > lastMaxIndex) {
                endEntity = lastMaxIndex;
                lastMaxIndex = startEntity;
            } else {
                annotatedText = annotatedText.substring(0, startEntity)
                    + '<span id="annot-' + entityIndex + '" class="label ' + type + '" style="cursor:hand;cursor:pointer;">'
                    + annotatedText.substring(startEntity, endEntity)
                    + '</span>'
                    + annotatedText.substring(endEntity, annotatedText.length + 1);
                lastMaxIndex = startEntity;
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
                url: '/processLongSentences',
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