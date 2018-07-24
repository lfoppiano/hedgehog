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

lang=result[0]["language"]["lang"]
entities_ = result[0]['entities']
for entity in entities_:
    outEntity = {}
    # Write 'header' content
    for headerElement in header:
        if headerElement in entity:
            outEntity[headerElement] = entity[headerElement]
        else:
            outEntity[headerElement] = ''
    outEntity['preferredTerm'] = hf.fetchPreferredTerm(entity=entity, lang=lang)
    outEntity['predictedClass'] = hf.fetchPredictedClass(entity=entity,lang=lang)

    toCSV.append(outEntity)

## Writing CSV
import csv

with open(output + ".csv", 'w') as csvOutput:
    writer = csv.DictWriter(csvOutput, toCSV[0].keys())
    writer.writeheader()
    writer.writerows(toCSV)

## Output HTML
indexText = len(string)
html = ''

for i in reversed(range(0, len(entities_))):
    entity = entities_[i]
    start = entity['offsetStart']
    end = entity['offsetEnd']

    while indexText > end:
        indexText = indexText - 1
        html = string[indexText] + html

    html = '<mark>' + string[start:end] + '</mark>' + html

    indexText = start

with open(output + ".html", 'w') as htmlOutput:
    htmlOutput.write('<html><header><meta charset="utf-8"/></header><body>\n'
                     + html
                     + '\n</body></html>')
