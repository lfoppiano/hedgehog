# Usage: historyBatch.py input output

import sys

from nerd.nerd import NerdClient

from HistoryFishing import HistoryFishing
from splitLeoHamon import SplitLeoHamon

hf = HistoryFishing()

if len(sys.argv) != 3:
    sys.exit("Not enough args. Usage: historyBatch.py input output")

input = sys.argv[1]
output = sys.argv[2]

client = NerdClient()

### Split and clean
leoHamonSplitter = SplitLeoHamon()
paragraphs = leoHamonSplitter.split(input)

### Analysis
string = leoHamonSplitter.toString(paragraphs)
result = client.disambiguateText(string)


### Writing output
## Preprocessed text
with open(output + ".raw", 'a') as rawOutput:
    rawOutput.write(string)

## Entities
header = ['rawName', 'type', 'offsetStart', 'offsetEnd', 'nerd_selection_score', 'wikipediaExternalRef', 'wikidataId']

toCSV = []
for entity in result[0]['entities']:
    outEntity = {}
    for headerElement in header:
        if headerElement in entity:
            outEntity[headerElement] = entity[headerElement]
        else:
            outEntity[headerElement] = ''
    outEntity['preferredTerm'] = hf.fetchPreferredTerm(entity=entity, lang="en")
    outEntity['predictedClass'] = hf.fetchPredictedClass(entity=entity,lang="fr")
    toCSV.append(outEntity)

import csv

with open(output + ".csv", 'w') as csvOutput:
    writer = csv.DictWriter(csvOutput, toCSV[0].keys())
    writer.writeheader()
    writer.writerows(toCSV)
