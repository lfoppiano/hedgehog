import sys
from bs4 import BeautifulSoup

# if len(sys.argv) != 3:
#     sys.exit("Not enough args. Usage: historyBatch.py input output")

# input directory
input = sys.argv[1]

# output directory
# output = sys.argv[2]

listEntities = [("Pope", 'PERSON'), ("Darth Wader", 'PERSON'), ('Clamart', 'LOCATION')]

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
