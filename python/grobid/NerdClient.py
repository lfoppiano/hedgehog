import requests


class NerdClient:
    nerdLocation = "http://cloud.science-miner.com/nerd/service/processNERDQuery"

    def processText(self, text):
        body = {
            "text": text,
            "language": {
                "lang": "en"
            },
            "entities": [],
            "resultLanguages": ["fr", "de", "en"],
            "onlyNER": "false",
            "sentence": "false",
            "format": "JSON",
            "customisation": "generic"
        }
        requests.headers['Content-Type'] = 'application/json; charset=UTF-8'
        r = requests.post(self.nerdLocation, json=body)
        # print("NERD response: " + str(r.status_code) + " in " + str(r.elapsed))

        statusCode = r.status_code
        nerdResponse = r.reason
        if statusCode == 200:
            nerdResponse = r.json()

        return nerdResponse, statusCode

    def getNerdLocation(self):
        return self.nerdLocation
