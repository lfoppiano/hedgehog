# coding: utf-8
# Big problem with the encoding
paragraphs=[]
with open("../../../Documents/OCR/Leo-Hamon-8-1944-tapuscrit/Leo-Hamon-8-1944-tapuscrit.txt") as f:
    #I split the texte in paragraphs first
    f = f.read().split("\n\n")
    #This removes the lines with the page numbers
    f[:] = [tup for tup in f if not tup.startswith("-") and not tup.endswith("-")]
    f[:] = [tup for tup in f if not tup.startswith(" ...") and not tup.endswith("...")]

    #This, in theory, will merge line finishing with ¬\n with the following paragraph
    for i in range(len(f)):
        if f[i].endswith('¬\n'):
            f[i:i+1] = [''.join(f[i:i+1])]

    for paragraph in f:
        #if paragraph.endswith('¬\n'):
        cleanParagraph=paragraph.replace("¬\n","").replace("-\n","").replace("\n"," ")
        paragraphs.append(cleanParagraph)
        # for line in paragraph:
        #     cleanLine = line  # .replace('\n', '')
        #     if cleanLine.startswith('-') and cleanLine.endswith('-\n'):
        #         continue
        #
        #     if cleanLine.endswith('-\n') or cleanLine.endswith('¬\n'):
        #         cleanLine[0:len(line) - 2]