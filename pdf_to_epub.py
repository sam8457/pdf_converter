#! python3

import re
from ebooklib import epub
from io import BytesIO
from pypdf import PdfReader # requires pillow for images

INPUT_FILE_NAME = "Problem.pdf"
OUTPUT_FILE_NAME = "The Problem of Political Authority (Huemer, Michael).epub"
TITLE = "The Problem of Political Authority"
AUTHOR = "Michael Huemer"
BLACKLIST = [
    # Author
    # Title
]
# Regex examples:
# "Chapter [0-9]+" # captures any number of digits
# "[0-9](?!.)" # (?![expression]) excludes anything that matches [expression]
CHAPTER_REGEX = [
    "Preface",
    "Analytical Contents",
    "List of Figures",
    "Part",
    "[0-9](?!.)"
]
COVER_PAGE_INDEX = 0 # typically should be 0
CHAPTER_LINE_INDEX = 0 # typically should be 0

reader = PdfReader(INPUT_FILE_NAME)

# add metadata
book = epub.EpubBook()
book.set_identifier(OUTPUT_FILE_NAME + "_cleaned")
book.set_title(TITLE)
book.set_language('en')
book.add_author(AUTHOR)
bookSpineList = ['cover','nav']
bookToc = ["Intro.xhtml"]

# add cover image
cover = reader.pages[COVER_PAGE_INDEX].images[0].data
book.set_cover("cover.jpg", cover)

# add css
style = '''
p{
    text-indent: 50px;
    margin: 0;
}
'''
css = epub.EpubItem(
    uid="style",
    file_name="style/styles.css",
    media_type="text/css",
    content=style)
book.add_item(css)

# Init first chapter
chapter = epub.EpubHtml(
    title="Intro",
    file_name=("Intro.xhtml"),
    lang='en'
)
content = f'<html><body><h1>Intro</h1><p>'

for pageNumber, page in enumerate(reader.pages):

    pageLines = page.extract_text().split('\n')

    # remove tabs
    #for i in range(len(pageLines)):
    #    pageLines[i] = pageLines[i].replace("\t", " ")

    for pattern in CHAPTER_REGEX:

        if len(pageLines) < CHAPTER_LINE_INDEX + 1:
            break

        match = re.search(pattern, pageLines[CHAPTER_LINE_INDEX])

        if match and match.start() <= 2:

            # Add chapter to book
            content += "</body></html>"
            chapter.set_content(content)
            print(chapter)
            chapter.add_item(css)
            book.add_item(chapter)
            bookSpineList.append(chapter)

            # Start a new chapter
            chapterTitle = pageLines[CHAPTER_LINE_INDEX]
            chapter = epub.EpubHtml(
                title=chapterTitle,
                file_name=(chapterTitle + ".xhtml"),
                lang='en'
            )
            content = f'<html><body><h1>{chapterTitle}</h1><p>'

    # add page's images
    try:
        for image in page.images:

            if pageNumber == 0:
                break

            imgFileName = 'images/pg' + str(pageNumber) + "_" + image.name

            book.add_item(epub.EpubImage(
                uid='image_1',
                file_name=imgFileName,
                media_type='image/gif',
                content=image.data
            ))

            content += f"<p><img src={imgFileName}></p>"
    except:
        print("Image error.")

    # add page's text
    for line in pageLines:

        #print(line)

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
        if firstChar.isnumeric():
            #print("Excluding: " + line)
            continue

        lastChar = line.strip()[-1]

        # Removes words that are broken across lines by hyphens
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
chapter.add_item(css)
book.add_item(chapter)
bookSpineList.append(chapter)

book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

book.toc = (
    epub.Link('toc.xhtml', 'Table of Contents', 'toc'),
    (epub.Section('Chapters'),
    (bookSpineList))
)

book.spine = bookSpineList

epub.write_epub(OUTPUT_FILE_NAME, book, {})

print("Done.")

# High priority:

# Format as functions

# Todo: Remove chapter titles being duplicated in paragraph text



# Low priority:

# Format images better

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
