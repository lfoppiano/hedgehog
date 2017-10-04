import requests


class ParserClient:
    clientLocation = "https://lindat.mff.cuni.cz/services/udpipe/api/process"

    models = {
        "en": "english",
        "es": "spanish-ancora",
        "fr": "french",
        "de": "german"
    }

    def process(self, text, lang):
        lang = self.models[lang]

        if not lang and not self.models[lang]:
            lang = self.models["en"]

        data = {'data': text, 'tokenizer': 'normalized_spaces;ranges', 'model': lang, 'parser': 'true',
                'tagger': 'true'}

        r = requests.post(self.clientLocation, data)

        statusCode = r.status_code
        message = r.reason

        if statusCode == 200:
            response = r.json()['result']
        else:
            response = str(statusCode) + ": " + message

        return response