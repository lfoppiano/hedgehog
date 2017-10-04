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


def getPreferredName(entity):
    name = ""

    if 'preferredTerm' in entity:
        name = entity['preferredTerm']

    return name


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


lang = 'en'

if 'language' in nerdResponse:
    lang = nerdResponse['language']['lang']

print("Language: " + lang)

if 'entities' in nerdResponse:
    print('Found %d entities' % len(nerdResponse['entities']))

    # Collect all the entities
    for entity in nerdResponse['entities']:
        # print(entity['rawName'])

        if 'type' in entity and entity['type'] in classesNERD:
            preferredName = getPreferredName(entity)
            rawName = getRawName(entity)
            print("NAME[NER]: " + preferredName + ", " + rawName + " [" + entity['type'] + "]")
            print("start: " + str(entity['offsetStart']) + " end: " + str(entity['offsetEnd']))
        else:
            name = getPreferredName(entity)
            raw_name = getRawName(entity)
            print("NAME[ERD]: " + str(name) + ", " + str(raw_name))
            print("start: " + str(entity['offsetStart']) + " end: " + str(entity['offsetEnd']))

        # CR
        # Converted entity['wikipediaExternalRef'] in string
        if 'wikipediaExternalRef' in entity:
            concept, conceptStatus = nerdClient.fetchConcept(str(entity['wikipediaExternalRef']), lang)

            if conceptStatus == 200:
                print("Categories: ")
                for category in concept['categories']:
                    print(str(category['category']) + ", ")

        Nentity = entity['rawName']
        offsetS = entity['offsetStart']

        sentence = nerdResponse['sentences']

        POStext = ""
        for i in range(0, len(sentence)):
            startt = int(sentence[i]['offsetStart'])
            endd = int(sentence[i]['offsetEnd'])

            r = range(startt, endd)
            if offsetS in r:
                POStext = text[startt:endd]
                # print(POStext.find(entity['rawName']))

        if len(POStext) == 0:
            print("Cannot find the sentence for the entity " + Nentity)
            sys.exit(-1)

        parserResponse = parserClient.process(POStext, lang)

        reader = CoNLLReader()
        sentences = reader.read_conll_u(parserResponse.split("\n"))

        subjects = []

        for s in sentences:
            for nodeId in s.nodes():
                # print(s.node[nodeId])
                if s.node[nodeId]['form'] == Nentity:
                    # We've found the node corresponding to the entity
                    for h, d in s.edges():
                        #Head
                        if d == nodeId:
                            print("head edge: " + str(s[h][d]))
                            print("head node: " + str(s.node[h]['form']))
                            continue

                        ## Dependants
                        elif h == nodeId:
                            print("dependent edge: " +str(s[h][d]))
                            print("dependent node: " + str(s.node[d]['form']))


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
