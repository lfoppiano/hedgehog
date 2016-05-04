import hashlib
import xml.etree.ElementTree as ET
from sys import argv

import requests
from bottle import route, request, run, static_file, response

# Configuration
from python.XmlStrategies import GenericItemStrategy

nerdLocation = "http://cloud.science-miner.com/nerd/service/processNERDQuery"
geoLocationLocation = "api.geonames.org/search?username=demo&q="

strategies = {
    # 'person': PersonStrategy(),
    'generic': GenericItemStrategy()
    # 'location': LocationStrategy(),
}


@route('/info')
def info():
    returnText = "Configuration: \n\t- nerdLocation: " + nerdLocation + " \n\t- Geo Location: " + geoLocationLocation

    return returnText


@route('/<filename:path>')
def server_static(filename):
    return static_file(filename, root='webapp')


@route('/nerd', method='POST')
def nerd():
    text = request.json["text"]

    body = {
        "text": text,
        "language": {
            "lang": "en"
        },
        "entities": [],
        "resultLanguages": ["fr", "de"],
        "onlyNER": "false",
        "sentence": "false",
        "format": "JSON",
        "customisation": "generic"
    }

    r = requests.post(nerdLocation, json=body)
    print("NERD response: " + str(r.status_code))

    geoLocations = []

    if r.status_code == 200:
        nerdResponse = r.json()

        if 'entities' in nerdResponse.keys():
            for entity in nerdResponse['entities']:
                if entity['type'] == "LOCATION":
                    placeName = entity['rawName']
                    geo = requests.get(geoLocationLocation, params={'username': 'demo', 'q': placeName})

                    print("GEO gazetteer response for query " + placeName + ": " + str(geo.status_code))

                    if geo.status_code == 200:
                        locationResponseJson = geo.json();
                        for location in locationResponseJson:
                            item = locationResponseJson[location][0];
                            geoLocations.append(
                                {
                                    'rawName': location,
                                    'name': item['name'],
                                    'country': item['countryCode'],
                                    'coordinates': {
                                        'longitude': item['longitude'],
                                        'latitude': item['latitude']
                                    }
                                }
                            );
                    else:
                        geoLocations[location] = "no location resolved in the Gazetteer";

    else:
        geoLocations = {'error': r.status_code}

    return {'locations': geoLocations}


@route('/nerd', method='POST')
def teiBuilderNerd():
    text = request.json["text"]

    l = []
    body = {
        "text": text,
        "language": {
            "lang": "en"
        },
        "entities": l,
        "resultLanguages": ["fr", "de"],
        "onlyNER": "false",
        "sentence": "false",
        "format": "JSON",
        "customisation": "generic"
    }

    r = requests.post(nerdLocation, json=body)

    response.headers['Content-Type'] = 'xml/application'
    print("NERD response: " + str(r.status_code))

    root = ET.Element("TEI")
    standOff = ET.SubElement(root, "standOff")
    text = ET.SubElement(root, "text")
    body = ET.SubElement(text, "body")

    if r.status_code == 200:
        nerdResponse = r.json()
        tmpText = nerdResponse['text']
        m = hashlib.md5()
        m.update(tmpText.encode('utf-8'))
        textId = m.hexdigest()
        p = ET.SubElement(body, "p", attrib={"xml:id": textId})
        p.text = tmpText

        annotations = {}

        if 'entities' in nerdResponse.keys():
            for entity in nerdResponse['entities']:
                type = str(entity['type']).lower()
                if type not in annotations.keys():
                    annotations[type] = []

                annotations[type].append(entity)

        for key in annotations.keys():
            strategy = strategies.get(key)
            if strategy is None:
                strategy = strategies['generic']
            standOff.append(strategy.transform(annotations[key], type, textId))

        string = ET.tostring(root, encoding="utf8", method='xml')

        return string


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
