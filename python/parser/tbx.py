# coding: utf-8
from bs4 import BeautifulSoup


class tbx:
    list = []

    def load(self, sourceDictionary):
        with open(sourceDictionary) as tbx:
            soup = BeautifulSoup(tbx, "xml")
        return soup

    def matchEntities(self, text, sourceDictionary, i):

        soup = self.load(sourceDictionary)

        namedEntitiesTBX = []
        id = i + 1
        langSecs = soup.find_all("langSec")
        for form in langSecs:
            preferredName = form.find("form", {"type": "lemma"}).text.replace("\n", " ").replace("\r", "").strip()
            orths = form.find_all("orth")
            for orth in orths:
                rawName = orth.text
                if rawName:
                    if text.find(rawName) is not -1:
                        offsetStart = text.find(rawName)
                        offsetEnd = text.find(rawName) + len(rawName)
                        namedEntity = {
                            "id": id,
                            "rawName": rawName,
                            "preferredName": preferredName,
                            "wikipediaExternalRef": "",
                            "offsetStart": offsetStart,
                            "offsetEnd": offsetEnd
                        }
                        namedEntitiesTBX.append(namedEntity)
                        id = id + 1

        return namedEntitiesTBX


# test
# t = tbx()
# dictionary = "../../resources/WW2_glossary.xml"
# text = "Diné le soir avec Pontaut et Auger. Nous nous demandions si nous devions faire quelque chose en tant qu'anciens P.C. Pontaut est assez enclin à l'admettre. On parle de la dernière attaque de Villon contre Frenay. Auger qui l'a connu parle de lui avec une sympathie qu'il a inspiré à tous ses collaborateurs."
# print(t.matchEntities(text, dictionary, 99))
