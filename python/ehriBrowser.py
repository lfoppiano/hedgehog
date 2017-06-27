from sys import argv

from bottle import route, run, static_file, response
from pymongo import MongoClient

from client.NerdClient import NerdClient

nerdClient = NerdClient()

client = MongoClient('localhost', 27017)
rawDatabase = client.get_database('ehri_solr')
nerdDatabase = client.get_database('ehri_nerd')

documentaryUnitNERDItems = ['findingAids_t', 'corporateBodies', 'locationOfOriginals_t',
                            'name', 'archivalHistory', 'subjects', 'repositoryName', 'biographicalHistory',
                            'scopeAndContent', 'archivistNote_t', 'countryName']

documentaryUnitERDItems = ['accessPoints', 'creator', 'places']

historicalAgentNERDItems = ['name']

@route('/ehri/documentaryUnit/<id>', method='GET')
def getDescription(id):
    rawCollection = rawDatabase.get_collection('documentaryUnit')
    nerdCollection = nerdDatabase.get_collection('documentaryUnit')

    response.headers['Content-Type'] = 'application/json'

    document = rawCollection.find_one({'itemId': id})
    if not document:
        response.status = 404
        response.content_type = 'text/html'
        return "Cannot find the documentary unit with id " + str(id)

    id = document['_id']
    # del document['_id']
    document['_id'] = str(document['_id'])  # ObjectID is not JSON serializable

    for item in document.items():
        if item[0] in documentaryUnitNERDItems:
            if type(item[1]) is list:
                for index, elem in enumerate(item[1]):
                    nerdResponse, statusCode = nerdClient.processText(elem)

                    if statusCode == 200:
                        if 'entities' in nerdResponse:
                            elem = {'raw': elem, 'nerdResponse': nerdResponse}
                            document[item[0]][index] = elem
                            # print(nerdResponse)
                            # print(elem)

                    else:
                        print("Error from NERD: " + str(statusCode) + ", for input " + str(item[0]) + ": " + str(elem))

            else:
                nerdResponse, statusCode = nerdClient.processText(item[1])

                if statusCode == 200:
                    if nerdResponse:
                        if 'entities' in nerdResponse:
                            elem = {'raw': item[1], 'nerdResponse': nerdResponse}
                            document[item[0]] = elem

                else:
                    print("Error from NERD: " + str(statusCode) + ", " + nerdResponse + ", for input " + str(
                        item[0]) + ": " + str(item[1]))

    return document


@route('/ehri/historicalAgent/<id>', method='GET')
def getDescription(id):
    response.headers['Content-Type'] = 'application/json'
    collection = rawDatabase.get_collection('historicalAgents')

    document = collection.find_one({'itemId': id})
    if not document:
        response.status = 404
        response.content_type = 'text/html'
        return "Cannot find the documentary unit with id " + str(id)

    document['_id'] = str(document['_id'])  # ObjectID is not JSON serializable

    for item in document.items():
        print(item)

    return document


@route('/<filename:path>')
def server_static(filename):
    return static_file(filename, root='webapp')


if len(argv) == 3:
    port = argv[2]
    host = argv[1]
elif len(argv) == 2:
    port = argv[1]
    host = '0.0.0.0'
else:
    print("Not enough parameters")
    exit(-1)

run(host=host, port=port, debug=True)
