#coding: utf-8
import sys
import json

from client.NerdClient import NerdClient
from client.ParserClient import ParserClient
from parser.conll import ConllReader

nerdClient = NerdClient()
parserClient = ParserClient()

text = """
Suite de la tournée des relations d'avant-guerre. J'ai aperçu mon plombier - il y a une véritable joie à retrouver des relations d'autrefois, après quatre années de coupure et de se sentir à l'unisson sur Pétain. Quand il m'en a parlé j'ai hésité à répondre catégoriquement, pour ne pas les choquer et j'ai dit : c'est un pauvre homme. Quel déchaînement : elle m'a dit c'est ainsi que vous appelez un homme qui nuit à son pays, etc... etc...
Cette femme, très simple, est vraiment épatante. Elle m'explique que depuis le début elle écoute les informations de la radio anglaise et les diffuse dans le quartier. Je leur demande s'ils sont affiliés à une organisation - Oui - Laquelle "la résistance " C'sst ici que parle le bon sens et la clairvoyance : au sommet on se bat pour des initiales, à la base on croit en la résistance.
On y croit avec plus de lucidité que de prétendus experts.
Cet homme était de droite autrefois ; Il m'explique que parmi les riches il y en a beaucoup qui ne sont pas avec nous, parce qu'ils craignant pour leur gros sous. Ils n'ont d'ailleurs pas renié leur origine, elle me parle de la fierté qu'elle éprouve à retrouver beaucoup de catholiques dans la résistance.
Nous parlons d'autres voisins du quartiers que sont-ils devenus. Celui-là vous savez c'est un français... et ça veut tout dire. Elle a raison cela veut tout dire - la droits a éclaté au feu de la guerre - il y a d'un côté les Français, plombiers ou hommes de lettres, et de l'autre ceux qui pensent à leurs gros sous...
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


    for entity in nerdResponse['entities']:
        #print(entity['rawName'])
        
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

        #CR
        #Converted entity['wikipediaExternalRef'] in string
        if 'wikipediaExternalRef' in entity:
            concept, conceptStatus = nerdClient.fetchConcept(str(entity['wikipediaExternalRef']), lang)
            if conceptStatus == 200:
                print("Categories: ")
                for category in concept['categories']:
                    print(str(category['category']) + ", ")

        offsetS = entity['offsetStart']
        


        sentence = nerdResponse['sentences']

        for i in range(0,len(sentence)):
            startt = int(sentence[i]['offsetStart'])
            endd = int(sentence[i]['offsetEnd'])

            r=range(startt,endd)
            if offsetS in r:
                POStext= text[startt:endd]
                # print(POStext.find(entity['rawName']))

                parserResponse = parserClient.process(POStext,"fr")
                
                reader = conll.CoNLLReader()
                sentences = reader.read_conll_u(parserResponse.split("\n"))

                subjects = []

                for s in sentences:
                    for h, d in s.edges():
                        print(str(s[h][d]))
                        if s[h][d]["deprel"] == 'nsubj':
                            subjects.append(s.node[d])