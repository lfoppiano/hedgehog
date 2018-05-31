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

# Writing output