import requests


class NerdOldClient:
    nerdLocation = "http://cloud.science-miner.com/nerd/service"
    nerdQueryUrl = nerdLocation + "/processNERDQuery"

    def processText(self, text, lang):
        text = text.replace("\n", "").replace("\r", "")
        body = {
            "text": text,
            "language": {
                "lang": lang
            },
            "entities": [],
            "resultLanguages": ["fr", "de", "en"],
            "onlyNER": "false",
            "sentence": "false",
            "format": "JSON",
            "customisation": "generic"
        }
        r = requests.post(self.nerdQueryUrl, query=body, headers={'Content-Type': 'application/json; charset=UTF-8'})
        # print("NERD response: " + str(r.status_code) + " in " + str(r.elapsed))

        statusCode = r.status_code
        nerdResponse = r.reason
        if statusCode == 200:
            nerdResponse = r.json()

        return nerdResponse, statusCode

        def processText(self, text):
            return processText(text, "en")

    def termDisambiguation(self, terms):
        if isinstance(terms, str):
            terms = [terms, 'history']

        body = {
            "termVector": [],
            "nbest": 0
        }

        for term in terms:
            body["termVector"].append({"term": term})

        r = requests.post(self.nerdQueryUrl, json=body, headers={'Content-Type': 'application/json; charset=UTF-8'})

        statusCode = r.status_code
        nerdResponse = r.reason
        if statusCode == 200:
            nerdResponse = r.json()

        return nerdResponse, statusCode

    def getNerdLocation(self):
        return self.nerdQueryUrl
