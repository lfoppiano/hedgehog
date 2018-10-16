# coding utf-8
import sys
import os
from bs4 import BeautifulSoup
from nerd.nerd import NerdClient

from edgehog.HistoryFishing import HistoryFishing

client = NerdClient()
hf = HistoryFishing()

# if len(sys.argv) != 3:
#     sys.exit("Not enough args. Usage: parser.py input output")

# input directory
input = sys.argv[1]


# output directory
# output = sys.argv[2]
def file_is_empty(path):
    return os.stat(path).st_size == 0


def listXMLfiles(directory):
    EADfiles = []  # liste fichiers
    for fileName in os.listdir(directory):
        pathFile = directory + "/" + fileName
        if file_is_empty(pathFile) == False:
            EADfiles.append(pathFile)
    return EADfiles


def load(file):
    # load XML files with Beautiful Soup
    with open(file) as ead:
        soup = BeautifulSoup(ead, "xml")
    return soup


# if workking with a directory as input
# files = (listXMLfiles(input))
# for file in files:

soup = load(input)
dids = soup.find_all('did')
listEntities = []

for did in dids:
    unittitles = did.find_all("unittitle")
    if unittitles != []:
        didTitles = ""
        for unittitle in unittitles:
            didTitles = didTitles + unittitle.get_text(strip=True) + " "

    didTitles = didTitles.replace('\xc2\xa0', ' ').replace('\xa0', ' ')
    result = client.disambiguateText(didTitles)

    if result[1] == 200:
        for entity in result[0]['entities']:
            if "type" in entity:
                wikidataId = ''
                if 'wikidataId' in entity:
                    wikidataId = entity["wikidataId"]

                listEntities.append(
                    {'rawName': entity["rawName"], 'class': entity["type"], 'wikidataId': wikidataId});

# header = ['rawName', 'type', 'offsetStart', 'offsetEnd', 'nerd_selection_score', 'wikipediaExternalRef', 'wikidataId']


# listEntities = [{'rawName': 'Pope', 'class':'PERSON', 'wikidataID': 'Q1234'}]

### Writing CSV ###
# import csv

# with open(output + ".csv", 'w') as csvOutput:
#   writer = csv.DictWriter(csvOutput, toCSV[0].keys())
# writer.writeheader()

soup = BeautifulSoup(open(input), 'xml')
archdesc = soup.ead.archdesc

controlAccess = soup.new_tag("controlaccess")
archdesc.insert(len(archdesc.contents), controlAccess)

# corpname, famname, function, genreform, geogname,name, occupation, persname, subject,


mapping = {
    # 'famname': ['PERSON'],
    # 'function': []
    # 'genreform',
    'geogname': ['LOCATION'],
    # 'name': ['PERSON'],
    # 'occupation':
    'persname': ['PERSON'],
    # 'subject': ['UNKNOWN', None, 'ARTIFACT', 'ANIMAL', 'PLANT', 'WEBSITE'],
    'corpname': ['BUSINESS', 'INSTITUTION', 'ORGANISATION']
}

inverseMapping = {}
for k, v in mapping.items():
    for x in v:
        inverseMapping.setdefault(x, []).append(k)

for entity in listEntities:
    tag = inverseMapping.get(entity['class'])
    if tag is None:
        tag = 'subject'
    attrs = {}
    if len(entity['wikidataId']) > 0:
        attrs = {'authfilenumber': entity['wikidataId']}

    entityTag = soup.new_tag(name=tag[0], attrs=attrs)
    entityTag.string = entity['rawName']
    controlAccess.append(entityTag)

print(archdesc)
# print(soup)
