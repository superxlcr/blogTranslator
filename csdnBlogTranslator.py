from urllib import request

from bs4 import BeautifulSoup

import tagProcessors
import utils

imgCounter = 0

dealingWithTableRow = 0
tableColumns = 0
missNewLine = False


def getTagAllContentsStr(tag):
    result = ""
    for content in tag.contents:
        if content.string is not None:
            result += content
    return result


def dealWithTagA(tagA):
    content = tagA.string
    href = tagA['href']
    if content == href:
        file.write(content)
    else:
        file.write("[{}]({})".format(content, href))


def dealWithTagImg(tagImg):
    global imgCounter
    imgCounter += 1
    file.write("![{}_pic{}]({})".format(tagImg['alt'], imgCounter, tagImg['src']))


def traverseContent(contentTag):
    global dealingWithTableRow
    global tableColumns
    global missNewLine
    for tag in contentTag.contents:
        if tag.name == 'h1':
            # <h1>
            file.write("# " + getTagAllContentsStr(tag))
        elif tag.name == 'h2':
            # <h2>
            file.write("## " + getTagAllContentsStr(tag))
        elif tag.name == 'img':
            # <img>
            dealWithTagImg(tag)
        elif tag.name == 'tbody':
            # <tbody>
            dealingWithTableRow = 0
            tableColumns = 0
            traverseContent(tag)
        elif tag.name == 'tr':
            if dealingWithTableRow == 1:
                file.write("|")
                for i in range(0, tableColumns):
                    file.write(" - |")
                file.write("\n")
            dealingWithTableRow += 1
            # <tr>
            file.write("| ")
            missNewLine = True
            traverseContent(tag)
            file.write("\n")
            missNewLine = False
            pass
        elif tag.name == 'td':
            # <td>
            tableColumns += 1
            traverseContent(tag)
            file.write(" | ")
        elif len(tag.contents) > 1 or len(tag.contents) == 1 and type(tag.contents[0]).__name__ != 'NavigableString':
            # deal with nesting tag
            traverseContent(tag)
        elif tag.name == 'a':
            # <a>
            dealWithTagA(tag)
        elif tag.name == 'br':
            # <br>
            file.write(" ")
        elif tag.name == 'code':
            # <code>
            file.write("```\n")
            file.write(tag.string)
            file.write("\n```")
        elif tag.name == 'p':
            # <p>
            if tag.string is not None:
                file.write(tag.string)
        elif tag.name == 'div':
            # <div>
            file.write(tag.string)
        elif tag.name == 'strong':
            # <strong>
            file.write("**{}**".format(tag.string))

            # todo use class write better


def translate_xml(url, writer):
    # net request
    print("do request with url : " + url)
    response = request.urlopen(url).read().decode('utf-8')
    soup = BeautifulSoup(response, 'html.parser')

    # write title
    utils.write_title(soup, writer)
    # write time
    utils.write_time(soup, writer)

    root_tag = soup.find_all('div', 'htmledit_views')
    root_processor = tagProcessors.build_tag_processor(writer)
    root_processor.process(root_tag)


if __name__ == '__main__':
    url_param, file_path = utils.check_params()
    writer = utils.get_writer(file_path)
    translate_xml(url_param, writer)
