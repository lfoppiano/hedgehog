#coding utf-8
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
    return os.stat(path).st_size==0


def listXMLfiles(directory):
    EADfiles = [] #liste fichiers
    for fileName in os.listdir(directory):
        pathFile = directory + "/" + fileName
        if file_is_empty(pathFile) == False:
            EADfiles.append(pathFile)
    return EADfiles



def load(file):
    #load XML files with Beautiful Soup
    with open(file) as ead:
        soup = BeautifulSoup(ead, "xml")
    return soup
# if workking with a directory as input
#files = (listXMLfiles(input))
#for file in files:

soup = load(input)
titles = soup.find_all('unittitle')

listEntities = []

for title in titles:
    string = repr(title.contents)
    result = client.disambiguateText(string)

    if result is not None:
        for entity in result[0]['entities']:
            if "type" in entity:
                listEntities.append((entity["rawName"], entity["type"]))
        #number of entities found


#header = ['rawName', 'type', 'offsetStart', 'offsetEnd', 'nerd_selection_score', 'wikipediaExternalRef', 'wikidataId']





## Writing CSV
#import csv

#with open(output + ".csv", 'w') as csvOutput:
 ##   writer = csv.DictWriter(csvOutput, toCSV[0].keys())
   # writer.writeheader()

soup = BeautifulSoup(open(input), 'xml')
archdesc = soup.ead.archdesc

controlAccess = soup.new_tag("controlaccess")
archdesc.insert(len(archdesc.contents), controlAccess)

## corpname, famname, function, genreform, geogname,name, occupation, persname, subject,


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

# print(inverseMapping)

for entity in listEntities:
    tag = inverseMapping.get(entity[1])
    if tag is None:
        tag = 'subject'
    entityTag = soup.new_tag(tag[0])
    entityTag.string = entity[0]
    controlAccess.insert_after(entityTag)

print(archdesc)
# print(soup)
