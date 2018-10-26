# coding utf-8
import sys
import os
from bs4 import BeautifulSoup
from nerd.nerd_client import NerdClient

from edgehog.HistoryFishing import HistoryFishing

client = NerdClient()
hf = HistoryFishing()

# if len(sys.argv) != 3:
#     sys.exit("Not enough args. Usage: parser.py input output")

# input directory
input = sys.argv[1]

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

header = ['rawName', 'class', 'wikidataId', 'preferredTerm']
for did in dids:
    unittitles = did.find_all("unittitle")
    if len(unittitles) > 0:
        didTitles = ""
        for unittitle in unittitles:
            didTitles = didTitles + unittitle.get_text(strip=True) + " "

        didTitles = didTitles.replace('\xc2\xa0', ' ').replace('\xa0', ' ')
        result = client.disambiguate_text(didTitles)

        if result[1] == 200:
            first_time = True
            controlAccess = None
            for entity in result[0]['entities']:
                if first_time:
                    controlAccess = soup.new_tag("controlaccess")
                    first_time = False

                out = {
                    'rawName': entity["rawName"]
                }

                if "type" in entity:
                    out['class'] = entity["type"]

                if 'wikidataId' in entity:
                    wikidataId = entity["wikidataId"]
                    preferredTerm = hf.fetchPreferredTerm(entity=entity, lang="fr")
                    predictedClass = hf.fetchPredictedClass(entity=entity, lang="fr")
                    out['predictedClass'] = predictedClass
                    out['wikidataId'] = wikidataId
                    out['preferredTerm'] = preferredTerm
                    # listEntities.append({'rawName': entity["rawName"], 'class': entity["type"], 'wikidataId': wikidataId, 'preferredTerm': preferredTerm, 'predictedClass': predictedClass});

                parent = did.parent
                parent.insert(len(parent.contents), controlAccess)

                if 'predictedClass' in out:
                    tag = inverseMapping.get(out['predictedClass'])
                elif 'class' in out:
                    tag = inverseMapping.get(out['class'])
                else:
                    tag = ['subject']

                if tag is None:
                    tag = ['subject']

                attrs = {}
                if 'wikidataId' in out and len(out['wikidataId']) > 0:
                    attrs = {'authfilenumber': out['wikidataId'], 'source':'wikidata'}

                entityTag = soup.new_tag(name=tag[0], attrs=attrs)

                if 'preferredTerm' in out:
                    entityTag.string = out['preferredTerm']
                else:
                    entityTag.string = out['rawName']
                controlAccess.append(entityTag)

# archdesc = soup.ead.archdesc


print(soup)

### Writing output
## Preprocessed text
with open("output" + ".xml", 'w') as rawOutput:
    rawOutput.write(str(soup))

# print(soup)

### Writing CSV ###
# import csv

# with open(output + ".csv", 'w') as csvOutput:
#   writer = csv.DictWriter(csvOutput, toCSV[0].keys())
# writer.writeheader()
