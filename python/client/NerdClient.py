import requests


class NerdClient:
    # nerdLocation = "http://localhost:8090/service"
    nerdLocation = "http://nerd.huma-num.fr/nerd"
    disambiguateService = nerdLocation + "/disambiguate"
    conceptService = nerdLocation + "/kb/concept"
    segmentationService = nerdLocation + "/segmentation"

    maxTextLength = 1

    def processText(self, text):
        text = text.replace("\n", "").replace("\r", "")

        sentenceCoordinates = [
            {
                "offsetStart": 0,
                "offsetEnd": len(text)
            }
        ]

        # Split text in sentences
        totalNbSentences = len(sentenceCoordinates)
        if len(text) > self.maxTextLength:
            statusCode, response = self.segmentate(text)

            if statusCode == 200:
                sentenceCoordinates = response['sentences']
                totalNbSentences = len(sentenceCoordinates)
            else:
                exit(-1)

            print("text too long, splitted in " + str(totalNbSentences) + " sentences. ")

        body = {
            "text": text,
            "entities": [],
            "resultLanguages": ["fr", "de", "en"],
            "onlyNER": "false",
            "customisation": "generic"
        }
        if totalNbSentences > 1:
            body['sentences'] = sentenceCoordinates

        sentencesGroups = []
        currentSentenceGroup = []
        for i in range(0, totalNbSentences):
            if i % 3 == 0:
                if len(currentSentenceGroup) > 0:
                    sentencesGroups.append(currentSentenceGroup)
                currentSentenceGroup = [i]
            else:
                currentSentenceGroup.append(i)

        if len(currentSentenceGroup) > 0:
            sentencesGroups.append(currentSentenceGroup)

        for group in sentencesGroups:
            body['processSentence'] = group

            files = {"query": str(body)}

            print(str(files))

            r = requests.post(self.disambiguateService, files=files, headers={'Accept': 'application/json'})

            statusCode = r.status_code
            nerdResponse = r.reason
            if statusCode == 200:
                nerdResponse = r.json()
                if 'entities' in nerdResponse:
                    body['entities'].extend(nerdResponse['entities'])

                    # if 'domains' in nerdResponse:
                    #     body['domains'].append(nerdResponse['entities'])

        return nerdResponse, statusCode

    def fetchConcept(self, id, lang="en"):
        url = self.conceptService + "/" + id + "?lang=" + lang
        r = requests.get(url, headers={'Accept': 'application/json'})

        statusCode = r.status_code
        nerdResponse = r.reason
        if statusCode == 200:
            nerdResponse = r.json()

        return nerdResponse, statusCode

    def termDisambiguation(self, terms):
        if isinstance(terms, str):
            terms = [terms, 'history']

        body = {
            "termVector": [],
            "nbest": 0
        }

        for term in terms:
            body["termVector"].append({"term": term})

        r = requests.post(self.disambiguateService, json=body,
                          headers={'Content-Type': 'application/json; charset=UTF-8'})

        statusCode = r.status_code
        nerdResponse = r.reason
        if statusCode == 200:
            nerdResponse = r.json()

        return nerdResponse, statusCode

    def getNerdLocation(self):
        return self.disambiguateService

    # Call the segmenter in order to split text in sentences
    def segmentate(self, text):

        files = {'text': text}
        r = requests.post(self.segmentationService, files=files)

        statusCode = r.status_code
        nerdResponse = r.reason
        if statusCode == 200:
            nerdResponse = r.json()

        return statusCode, nerdResponse
