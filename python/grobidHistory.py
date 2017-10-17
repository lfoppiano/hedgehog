# coding: utf-8
import sys

from client.NerdClient import NerdClient
from client.ParserClient import ParserClient
from parser.Conll import CoNLLReader

nerdClient = NerdClient()
parserClient = ParserClient()

text = """
L'extrême-gauche de la Résistance affiche un scepticisme critique. Je vois Yves qui m'avait cité l'impatience d'Alger devant le cas Pucheu comme une illustration de la crise du Gaullisme.
"""

classesNERD = ["LOCATION", "PERSON", "TITLE", "ACRONYM", "ORGANISATION", "INSTITUTION", "PERSON_TYPE"]
domains = []

print("Processing " + text)
nerdResponse, statusCode = nerdClient.processText(text)

if statusCode != 200:
    print("error " + str(statusCode))
    sys.exit()


def fetchPreferredTerm(entity):
    preferredTerm = ""

    if 'wikipediaExternalRef' in entity:
        concept, conceptStatus = nerdClient.fetchConcept(str(entity['wikipediaExternalRef']), lang)

        if conceptStatus == 200:
            if 'preferredTerm' in concept:
                preferredTerm = concept['preferredTerm']

    return preferredTerm


def getRawName(entity):
    name = ""
    if 'rawName' in entity:
        name = entity['rawName']

    return name


def getDomains(entity):
    domains = []
    if 'domains' in entity:
        domains = entity['domains']

    return domains


def collectEntities(entities, listEntitiesInSentence):
    result = []
    for i in listEntitiesInSentence:
        result.append(entities[i])

    return result


def extractPOS(text, lang, entities):
    # Parsing the sentence containing the entity -> result in CONLL
    parserResponse = parserClient.process(text, lang)

    # Parsing the CONLL result
    reader = CoNLLReader()
    sentences = reader.read_conll_u(parserResponse.split("\n"))

    results = {}

    # Get the head and the dependants of the entities
    for s in sentences:
        for e in entities:
            for nodeId in s.nodes():
                print(s.node[nodeId]['form'])
                if s.node[nodeId]['form'] == e['rawName']:
                    substrToken = "TokenRange="
                    tRange = str(s.node[nodeId]['misc'].split(substrToken)[1])
                    # We've found the node corresponding to the entity
                    dependents = []
                    head = ""

                    for h, d in s.edges():
                        # Head
                        if d == nodeId:
                            head = s[h][d]
                            head['form'] = str(s.node[h]['form'])
                            continue


                        ## Dependants
                        elif h == nodeId:
                            dep = (s[h][d])
                            dep['form'] = str(s.node[d]['form'])
                            dependents.append(dep)

                    results[e['id']] = (head, dependents)

    return results


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
        preferredTerm = fetchPreferredTerm(entity)
        rawName = getRawName(entity)
        offsetS = entity['offsetStart']
        offsetE = entity['offsetEnd']

        namedEntity = {
            "id": i,
            "rawName": rawName,
            "preferredName": preferredTerm,
            "wikipediaExternalRef": entity['wikipediaExternalRef'],
            "offsetStart": offsetS,
            "offsetEnd": offsetE
        }

        # If NER type present, I add it
        if 'type' in entity and entity['type'] in classesNERD:
            namedEntity['type'] = entity['type']

        namedEntities.append(namedEntity)
        i = i + 1

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
        entitiesInSentence = collectEntities(namedEntities, sentenceGroup[sentenceIndex])
        offsetStart = sentences[sentenceIndex]['offsetStart']
        offsetEnd = sentences[sentenceIndex]['offsetEnd']
        result = extractPOS(text[offsetStart:offsetEnd], lang, entitiesInSentence)

        for entityIndex in result.keys():
            head, dependencies = result[entityIndex]
            namedEntities[entityIndex]['dependencies'] = dependencies
            namedEntities[entityIndex]['head'] = head

print(namedEntities)



# if len(POStext) == 0:
#     print("Cannot find the sentence for the entity " + rawName)
#     sys.exit(-1)
#
#         extractPOS(POStext, lang, entity)
#
#         namedEntity = {
#             "rawName": rawName,
#             "preferredName": preferredName,
#             "tokenRange": tRange,
#             "wikipediaExternalRef": entity['wikipediaExternalRef'],
#             "head": head,
#             "dependents": dependents
#         }
#
#
#
# print(namedEntities)

# response = {
#   "sentence": POStext,
#  "namedEntities": namedEntities
# }

# print(response)

# if s[h][d]["deprel"] == 'nsubj':
#     subjects.append(s.node[d])



# @route('/subject', method='POST')
# def process():
#     success = False
#     params = request.params
#     if 'text' not in params:
#         return {'OK': success}
#
#     text = params["text"]
#     if 'lang' in params:
#         lang = params["lang"]
#     else:
#         lang = "en"
#
#     dependency = parserClient.process(text, lang)
#
# reader = CoNLLReader()
#     sentences = reader.read_conll_u(dependency.split("\n"))
#
#     subjects = []
#
#     for s in sentences:
#         for h, d in s.edges():
#             print(str(s[h][d]))
#             if s[h][d]["deprel"] == 'nsubj':
#                 subjects.append(s.node[d])
#
#     return subjects
