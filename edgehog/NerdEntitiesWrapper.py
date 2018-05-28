# coding: utf-8
import sys

from nerd.nerd import NerdClient


class NerdEntitiesWrapper:
    nerdClient = NerdClient()

    def fetchPreferredTerm(self, entity, lang):
        preferredTerm = ""

        if 'wikipediaExternalRef' in entity:
            concept, conceptStatus = self.nerdClient.fetchConcept(str(entity['wikipediaExternalRef']), lang)

            if conceptStatus == 200:
                if 'preferredTerm' in concept:
                    preferredTerm = concept['preferredTerm']

        return preferredTerm

    def getField(self, entity, field):
        name = ""
        if field in entity:
            name = entity[field]

        return name

    def process(self, text):
        print("Processing " + text)
        nerdResponse, statusCode = self.nerdClient.processText(text)

        if statusCode != 200:
            print("error " + str(statusCode))
            sys.exit()

        lang = 'en'

        if 'language' in nerdResponse:
            lang = nerdResponse['language']['lang']

        print("Language: " + lang)
        namedEntities = []

        # Working on the entities
        if 'entities' in nerdResponse:
            entityList = nerdResponse['entities']
            print('Found %d entities' % len(entityList))

            i = 0

            # Collect all the entities
            for entity in entityList:
                preferredTerm = self.fetchPreferredTerm(entity, lang)
                rawName = self.getField(entity, 'rawName')
                offsetS = entity['offsetStart']
                offsetE = entity['offsetEnd']

                namedEntity = {
                    "id": i,
                    "rawName": rawName,
                    "preferredName": preferredTerm,
                    "wikipediaExternalRef": self.getField(entity, 'wikipediaExternalRef'),
                    "offsetStart": offsetS,
                    "offsetEnd": offsetE
                }

                # If NER type present, I add it
                if 'type' in entity:
                    namedEntity['type'] = entity['type']

                    # if namedEntity['type'] in self.classesNERD:
                namedEntities.append(namedEntity)
                i = i + 1

        return namedEntities