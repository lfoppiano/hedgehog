# coding: utf8
# Split the Leo Hamon diary in paragraphs

import sys
import re


class SplitLeoHamon:

    def removeHypen(self, listText, index, skipNext=0):
        regex = re.search(r"[¬-]\s*$", listText[index])

        if regex is None:
            return listText[index], skipNext
        else:
            matching = regex.group()
            newText = listText[index][0:len(listText[index]) - len(matching)]
            skipNext = skipNext + 1

            (text, skipNext) = self.removeHypen(listText, index + 1, skipNext)

            return newText + text, skipNext

    def split(self, filePath):

        paragraphs = []
        with open(filePath) as f:
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

            # for i in range(len(cleanedText)):
            #     print(str(i) + "\t\t\t'" + cleanedText[i] + "'\n")

            cleanedText2 = []
            skipNext = 0

            for i in range(len(cleanedText)):
                if skipNext > 0:
                    skipNext = skipNext - 1
                    continue

                # Dehypenisation
                if i < len(cleanedText):
                    (processedString, computedSkipNext) = self.removeHypen(cleanedText, i, 0)
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

        return paragraphs

    def print(self, paragraphs):
        for paragraph in paragraphs:
            for sentence in paragraph:
                print(str(sentence))
            print("\n")

    def toString(selfs, paragraphs):
        output = ""
        for paragraph in paragraphs:
            output = output + ' '.join(paragraph)

        return output



if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("Missing parameter. Usage: python splitLeoHamon.py leohamon_text.txt")

    splitter = SplitLeoHamon()
    splitter.print(splitter.split(sys.argv[1]))
