# coding: utf-8
# Big problem with the encoding

## Split the LeoHamon diary in paragraphs

import sys

if len(sys.argv) != 2:
    sys.exit("Missing parameter. Usage: python splitLeoHamon.py leohamon_text.txt")

paragraphs = []
with open(sys.argv[1]) as f:
    # split the text in paragraphs first
    text = f.read()
    splittedText = text.split("\n")

    cleanedText = []
    previousLine = None
    for line in splittedText:

        if line.startswith("-") or line.endswith("-"):
            continue

        if line.startswith("...") or line.endswith("..."):
            continue

        if not previousLine == None:
            if previousLine == "\n" and line == "\n":
                continue
            cleanedText.append(previousLine)

        previousLine = line

    cleanedText.append(previousLine)

    for i in range(len(cleanedText)):
        if i < len(cleanedText):

            if cleanedText[i].endswith('¬'):
                cleanedText[i] = cleanedText[i][0:len(cleanedText[i]) - 1] + ' ' + cleanedText[i + 1]
                cleanedText.pop(i + 1)

            # if cleanedText[i] == "":
            #     cleanedText.pop(i)

    for paragraph in cleanedText:
        # if paragraph.endswith('¬\n'):
        cleanParagraph = paragraph.replace("¬\n", "").replace("-\n", "").replace("\n", " ")

    paragraphs.append(cleanParagraph)
    # for line in paragraph:
    #     cleanLine = line  # .replace('\n', '')
    #     if cleanLine.startswith('-') and cleanLine.endswith('-\n'):
    #         continue
    #
    #     if cleanLine.endswith('-\n') or cleanLine.endswith('¬\n'):
    #         cleanLine[0:len(line) - 2]
