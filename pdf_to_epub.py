#! python3

import re
from pypdf import PdfReader
from ebooklib import epub

INPUT_FILE_NAME = "Influence.pdf"
OUTPUT_FILE_NAME = "Influence.epub"
TITLE = "Influence"
AUTHOR = "Robert B. Cialdini Ph.D"
BLACKLIST = [
    #".{0}[1234567890]+.*", # Page numbers and footnotes #Edit: needs to only match first character in line, maybe remove
    "Robert B. Cialdini Ph.D / [1234567890]+", # Author
    "Robert B. Cialdini Ph.D / [ivx]+",
    "[1234567890]+ / Influence", # Title
    "[ivx]+ / Influence",
]
CHAPTER_REGEX = [
    "INTRODUCTION",
    "Chapter [1234567890]+"
]

# https://pypdf.readthedocs.io/en/stable/user/extract-text.html
reader = PdfReader(INPUT_FILE_NAME)

# https://docs.sourcefabric.org/projects/ebooklib/en/latest/tutorial.html#creating-epub
# https://github.com/aerkalov/ebooklib/blob/master/samples/01_basic_create/create.py
book = epub.EpubBook()
book.set_identifier(OUTPUT_FILE_NAME + "_cleaned")
book.set_title(TITLE)
book.set_language('en')
book.add_author(AUTHOR)
bookSpineList = ['nav']

# Init first chapter
chapter = epub.EpubHtml(
    title="Intro",
    file_name=("Intro.xhtml"),
    lang='en'
)
content = f'<html><body><h1>Intro</h1><p>'

for page in reader.pages:

    pageLines = page.extract_text().split('\n')

    for pattern in CHAPTER_REGEX:
        if re.search(pattern, pageLines[0]):

            # Add chapter to book
            content += "</body></html>"
            chapter.set_content(content)
            book.add_item(chapter)
            bookSpineList.append(chapter)

            # Start a new chapter
            chapterTitle = pageLines[0]
            chapter = epub.EpubHtml(
                title=chapterTitle,
                file_name=(chapterTitle + ".xhtml"),
                lang='en'
            )
            content = f'<html><body><h1>{chapterTitle}</h1><p>'

            
    for line in pageLines:

        if line.strip() == "":
            content += "<p></p>"
            continue

        # Skips common patterns (authors, titles, etc.)
        skipLine = False
        for pattern in BLACKLIST:
            if re.search(pattern, line):
                skipLine = True
        if skipLine:
            #print("Excluding: " + line)
            continue

        firstChar = line[0]

        # Skips page numbers and footnotes
        # Bug: sometimes catches legtimate lines that happen to start with a number
        # Bug: does not catch multi-line footnotes
        if firstChar.isnumeric():
            #print("Excluding: " + line)
            continue

        lastChar = line.strip()[-1]

        # Removes words that are broken across lines by hyphens
        # Bug: Sometimes catches hyphenated compound words that happen to span newlines
        if lastChar == "-":
            content += line.strip()[:-1]
            continue

        if len(line) < 2: # prevents out of index error
            continue
        secondToLastChar = line.strip()[-2]

        # Removes in-paragraph newlines
        if lastChar in "\"'“”":
            if secondToLastChar not in ":.!?—…":
                content += line.strip() + " "
                continue
        elif lastChar not in ":.!?…":
            content += line.strip() + " "
            continue
        
        # End of paragraph
        content += line.strip() + "</p><p>&#9;"

# Add final chapter to book
content += "</body></html>"
chapter.set_content(content)
book.add_item(chapter)
bookSpineList.append(chapter)

book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

book.spine = bookSpineList

epub.write_epub(OUTPUT_FILE_NAME, book, {})

print("Done.")

# Todo: Format pages better (tabs on newlines)

# Todo: Remove chapter titles being duplicated in paragraph text

# Todo: Extract images
# https://pypdf.readthedocs.io/en/stable/user/extract-images.html



# Low priority:

# Bug: legit lines that happen to start with numbers are excluded
    # Could check if value is superscripted
        # Would that work for all files?

# Bug: multi-line footnotes only exclude the first line
    # A fix to this could harm the previous bug more badly

# Todo: find a way to auto detect Author and Book Title
    # Maybe pre-scan the first N pages of the file to find the repeat lines?
    # And add them to the top of the output automatically

# Optional: place footnotes at end of file
    # Remove footnotes markers in paragraph if this is not done
