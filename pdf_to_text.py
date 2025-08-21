#! python3

import re
from pypdf import PdfReader

INPUT_FILE_NAME = "Influence.pdf"
OUTPUT_FILE_NAME = "Influence.txt"
BLACKLIST = [
    #".{0}[1234567890]+.*", # Page numbers and footnotes #Edit: needs to only match first character in line, maybe remove
    "Robert B. Cialdini Ph.D / [1234567890]+", # Author
    "Robert B. Cialdini Ph.D / [ivx]+",
    "[1234567890]+ / Influence", # Title
    "[ivx]+ / Influence",
]

# https://pypdf.readthedocs.io/en/stable/user/extract-text.html
reader = PdfReader(INPUT_FILE_NAME)
cleanBook = ""

for page in reader.pages:

    cleanPage = ""

    pageLines = page.extract_text().split('\n')
    for line in pageLines:
        
        if line.strip() == "":
            cleanPage += "\n"
            continue

        # Skips common patterns (authors, titles, etc.)
        skipLine = False
        for pattern in BLACKLIST:
            if re.search(pattern, line):
                skipLine = True
        if skipLine:
            print("Excluding: " + line)
            continue

        firstChar = line[0]

        # Skips page numbers and footnotes
        # Bug: sometimes catches legtimate lines that happen to start with a number
        # Bug: does not catch multi-line footnotes
        if firstChar.isnumeric():
            print("Excluding: " + line)
            continue

        lastChar = line.strip()[-1]

        # Removes words that are broken across lines by hyphens
        # Bug: Sometimes catches hyphenated compound words that happen to span newlines
        if lastChar == "-":
            cleanPage += line[:-1]
            continue

        if len(line) < 2: # prevents out of index error
            continue
        secondToLastChar = line.strip()[-2]

        # Removes in-paragraph newlines
        if lastChar in "\"'“”":
            if secondToLastChar not in ":.!?—…":
                cleanPage += (line.strip() + " ")
                continue
        elif lastChar not in ":.!?…":
            cleanPage += (line.strip() + " ")
            continue
        
        # End of paragraph
        cleanPage += (line.strip() + "\n\t")

    cleanBook += cleanPage

outputFile = open(OUTPUT_FILE_NAME, "w")
outputFile.write(cleanBook)
outputFile.close()
print("Done.")

# Bug: legit lines that happen to start with numbers are excluded
    # Could check if value is superscripted
        # Would that work for all files?

# Bug: multi-line footnotes only exclude the first line
    # A fix to this could harm the previous bug more badly

# Todo: Format headers better
    # Todo: add line break after chapter regex is matched
    # Maybe check if next line is capitalized?

# Todo: find a way to auto detect Author and Book Title
    # Maybe pre-scan the first N pages of the file to find the repeat lines?
    # And add them to the top of the output automatically

# Todo: Extract images
# https://pypdf.readthedocs.io/en/stable/user/extract-images.html

# Todo: Add support for other file types
    # Especially ones that support images

# Optional: place footnotes at end of file
    # Remove footnotes markers in paragraph if this is not done
