# coding: utf-8
# import sys
from nerd.nerd_client import NerdClient

import requests

from edgehog.client.ParserClient import ParserClient


class HistoryFishing:
    nerdClient = NerdClient()
    parserClient = ParserClient()

    classesNERD = ["LOCATION", "PERSON", "TITLE", "ACRONYM", "ORGANISATION", "INSTITUTION", "PERSON_TYPE"]
    domainsNERD = ["History"]
    domains = []

    def fetchPreferredTerm(self, entity, lang):
        preferredTerm = ""

        if 'wikipediaExternalRef' in entity:
            concept, conceptStatus = self.nerdClient.get_concept(str(entity['wikipediaExternalRef']), lang)
            if conceptStatus == 200:
                if 'preferredTerm' in concept:
                    preferredTerm = concept['preferredTerm']

                    return preferredTerm
        elif 'wikidataId' in entity:
            concept, conceptStatus = self.nerdClient.get_concept(str(entity['wikidataId']), lang)
            if conceptStatus == 200:
                for langs in concept['multilingual']:
                    if langs["lang"] == lang:
                        preferredTerm = langs["term"]
                if preferredTerm is None:
                    preferredTerm = concept['preferredTerm']
                return preferredTerm

    def fetchPredictedClass(self, entity, lang):
        predictedClass = ""
        urlBase = 'http://nerd.huma-num.fr/kid/service/ner?id='

        if 'wikidataId' in entity:

            request= urlBase+entity['wikidataId']
            r=requests.get(request)
            if r.status_code == 200:
                if 'predictedClass' in r.json():
                    predictedClass = r.json()['predictedClass']
                    return predictedClass
                else:
                    return ""

        elif 'wikipediaExternalRef' in entity:
            request = urlBase + entity['wikipediaExternalRef']
            r = requests.get(request)
            if r.status_code == 200:
                if 'predictedClass' in r.json():
                    predictedClass = r.json()['predictedClass']
                    return predictedClass
                else:
                    return ""

    def getField(self, entity, field):
        name = ""
        if field in entity:
            name = entity[field]

        return name

    def collectEntities(self, entities, listEntitiesInSentence):
        result = []
        for i in listEntitiesInSentence:
            result.append(entities[i])

        return result

    def extractPOS(self, text, lang, entities):
        # Parsing the sentence containing the entity -> result in CONLL
        parserResponse = self.parserClient.process(text, lang)

        # Parsing the CONLL result
        reader = CoNLLReader()
        sentences = reader.read_conll_u(parserResponse.split("\n"))

        results = {}

        # Get the head and the dependants of the entities
        for s in sentences:
            for e in entities:
                for nodeId in s.nodes():
                    # print(s.node[nodeId]['form'])
                    if s.node[nodeId]['form'] == e['rawName'] \
                            or e['rawName'].startswith(s.node[nodeId]['form']):
                        # We've found the node corresponding to the entity
                        dependents = []
                        head = {}

                        for h, d in s.edges():
                            # Head
                            if d == nodeId:
                                tmpHead = s[h][d]
                                head['form'] = str(s.node[h]['form'])
                                start, end = self.getRange(s.node[h])
                                head['offsetStart'] = start
                                head['offsetEnd'] = end
                                head['relation'] = tmpHead['deprel']
                                continue


                            # Dependants
                            elif h == nodeId:
                                tmpDep = s[h][d]
                                dep = {'form': str(s.node[d]['form'])}
                                start, end = self.getRange(s.node[d])
                                dep['offsetStart'] = start
                                dep['offsetEnd'] = end
                                dep['relation'] = tmpDep['deprel']
                                dependents.append(dep)

                        results[e['id']] = (head, dependents)

        return results

    def getRange(self, nodeId):
        substrToken = "TokenRange="
        if 'misc' in nodeId and 'TokenRange' in nodeId['misc']:
            tRange = nodeId['misc'].split(substrToken)

            split = str(tRange[1]).split(":")
            return split[0], split[1]
        return 0, 0

    def process(self, text):
        print("Processing " + text)
        nerdResponse, statusCode = self.nerdClient.processText(text)

        if statusCode != 200:
            print("error " + str(statusCode) + ": " + str(nerdResponse))
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

        # Matching with tbx dictionary
        # sourceDictionary = "resources/WW2_glossary.xml"
        # tbxEntities = tbx.matchEntities(text, sourceDictionary, i)
        # namedEntities.append(tbxEntities)

        # Working on the sentences
        sentences = nerdResponse['sentences']

        sentenceGroup = {}

        # Find the group of entities the current sentence contains
        for i in range(0, len(sentences)):
            startSentence = int(sentences[i]['offsetStart'])
            endSentence = int(sentences[i]['offsetEnd'])
            r = range(startSentence, endSentence)

            for entity in namedEntities:
                entityIndex = namedEntities.index(entity)
                if entity['offsetStart'] in r:
                    if i in sentenceGroup:
                        sentenceGroup[i].append(entityIndex)
                    else:
                        sentenceGroup[i] = [entityIndex]

        for sentenceIndex in sentenceGroup.keys():
            if len(sentenceGroup[sentenceIndex]) > 0:
                entitiesInSentence = self.collectEntities(namedEntities, sentenceGroup[sentenceIndex])
                offsetStart = sentences[sentenceIndex]['offsetStart']
                offsetEnd = sentences[sentenceIndex]['offsetEnd']
                result = self.extractPOS(text[offsetStart:offsetEnd], lang, entitiesInSentence)

                for entityIndex in result.keys():
                    head, dependencies = result[entityIndex]
                    head['offsetStart'] = int(head['offsetStart']) + int(sentences[sentenceIndex]['offsetStart'])
                    head['offsetEnd'] = int(head['offsetEnd']) + int(sentences[sentenceIndex]['offsetStart'])
                    namedEntities[entityIndex]['dependencies'] = dependencies
                    namedEntities[entityIndex]['head'] = head

        for entity in namedEntities:
            print("-> " + str(entity['rawName']))
            if 'head' in entity:
                print("\t\thead: " + str(entity['head']['form']) + " ==> " + str(entity['head']['relation']))
            if 'dependencies' in entity:
                for dep in entity['dependencies']:
                    print("\t\tdependency: " + str(dep['form']) + " ==> " + str(dep['relation']))

        return namedEntities
