# coding: utf8
## Split the Leo Hamon diary in paragraphs

import sys
import re

if len(sys.argv) != 2:
    sys.exit("Missing parameter. Usage: python splitLeoHamon.py leohamon_text.txt")


def removeHypen(listText, index, skipNext=0):
    regex = re.search(r"[¬-]\s*$", listText[index])

    if regex is None:
        return listText[index], skipNext
    else:
        matching = regex.group()
        newText = listText[index][0:len(listText[index]) - len(matching)]
        skipNext = skipNext + 1

        (text, skipNext) = removeHypen(listText, index + 1, skipNext)

        return newText + text, skipNext


paragraphs = []
with open(sys.argv[1]) as f:
    # split the text in paragraphs first
    text = f.read()
    splittedText = text.split("\n")

    cleanedText = []
    previousLine = None
    for line in splittedText:

        # Skip page number
        if line.startswith("-") and line.endswith("-"):
            continue

        # Skip specific markers
        if line.startswith("...") and line.endswith("..."):
            continue

        if previousLine is not None:
            if previousLine == "\n" and line == "\n":
                continue
            cleanedText.append(previousLine)

        previousLine = line

    cleanedText.append(previousLine)

    for i in range(len(cleanedText)):
        print(str(i) + "\t\t\t'" + cleanedText[i] + "'\n")

    cleanedText2 = []
    skipNext = 0

    for i in range(len(cleanedText)):
        if skipNext > 0:
            skipNext = skipNext - 1
            continue

        # Dehypenisation
        if i < len(cleanedText):
            (processedString, computedSkipNext) = removeHypen(cleanedText, i, 0)
            cleanedText2.append(processedString)
            skipNext = computedSkipNext

    # create paragraphs, separator in two blank lines.
    paragraph = []
    for i in range(len(cleanedText2)):
        if cleanedText2[i] != "":
            paragraph.append(cleanedText2[i])
        elif i + 1 < len(cleanedText2) and cleanedText2[i + 1] == "":
            paragraphs.append(paragraph)
            paragraph = []

            # if cleanedText[i] == "":
            #     cleanedText.pop(i)

    # for paragraph in cleanedText:
    # if paragraph.endswith('¬\n'):
    #   cleanParagraph = paragraph.replace("¬\n", "").replace("-\n", "").replace("\n", " ")

    # paragraphs.append(cleanParagraph)
    # for line in paragraph:
    #     cleanLine = line  # .replace('\n', '')
    #     if cleanLine.startswith('-') and cleanLine.endswith('-\n'):
    #         continue
    #
    #     if cleanLine.endswith('-\n') or cleanLine.endswith('¬\n'):
    #         cleanLine[0:len(line) - 2]

print(str(paragraphs.decode('string_escape')))
