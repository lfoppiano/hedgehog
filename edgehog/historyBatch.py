# Usage: historyBatch.py input output

import sys


from HistoryFishing import HistoryFishing

hf = HistoryFishing()

if len(sys.argv) != 3:
    sys.exit("Not enough args. Usage: historyBatch.py input output")

input = sys.argv[1]
output = sys.argv[2]

# a = NerdClient(apiBase="http://nerd.huma-num.fr/nerd")
a = NerdClient()
print(a.disambiguatePdf(output))
# print(a.disambiguateText("This is a sentence written in Washington, and computed in Milan Rome and Ancona. ", "it"))



sys.exit()


### Processing input
paragraphs = []
with open(input) as f:
    for line in f:
        cleanLine = line #.replace('\n', '')
        if cleanLine.startswith('-') and cleanLine.endswith('-\n'):
            continue
            
        if cleanLine.endswith('-\n') or cleanLine.endswith('¬\n'):
            cleanLine[0:len(line)-1]

### Analysis

#hf.process()

### Writing output
