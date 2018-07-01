import re
import sys
from urllib import request

from bs4 import BeautifulSoup

import utils

CSDN_BLOG_STR = str("blog.csdn.net")
PARAM_LENGTH = 3
file = None
imgCounter = 0


def dealWithTagA(tagA):
    global file
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


def traverseContent(contentTag, recursiveCounter):
    for tag in contentTag.contents:
        if type(tag).__name__ == 'NavigableString':
            file.write(tag.string)
        elif len(tag.contents) > 0 and type(tag.contents[0]).__name__ != 'NavigableString':
            traverseContent(tag, recursiveCounter + 1)
        elif utils.isTagA(tag):
            dealWithTagA(tag)
        elif utils.isTagBr(tag):
            file.write(" ")
        elif utils.isTagImg(tag):
            dealWithTagImg(tag)
        elif utils.isTagCode(tag):
            file.write("```\n")
            file.write(tag.string)
            file.write("\n```")
        elif utils.isTagP(tag):
            if tag.string != None:
                file.write(tag.string)

        if recursiveCounter == 0:
            file.write("\n")


def doTranslate():
    global file
    # net request
    url = sys.argv[1]
    print("do request with url : " + url)
    response = request.urlopen(url).read().decode('utf-8')
    # file.write(response)

    soup = BeautifulSoup(response, 'html.parser')

    title = soup.find_all('h1', 'title-article')[0].string
    file.write("title : " + title + "\n")

    timeStr = soup.find_all('span', 'time')[0].string
    timePattern = re.compile(r'(\d{4}).?(\d{2}).?(\d{2}).*(\d{2}).?(\d{2}).?(\d{2})')
    timeMatch = timePattern.match(timeStr)
    file.write("time : {}-{}-{} {}:{}:{}\n\n".format(timeMatch.group(1), timeMatch.group(2), timeMatch.group(3),
                                                     timeMatch.group(4), timeMatch.group(5), timeMatch.group(6)))

    contentTag = soup.find_all('div', 'htmledit_views')
    traverseContent(contentTag[len(contentTag) - 1], 0)


def checkParamAndOpenFile():
    global file
    # check param length
    length = len(sys.argv)
    if length != PARAM_LENGTH:
        print("usage : python csdnBlogTranslator.py csdn_url output_file_path")
        exit(0)

    # check param
    url = sys.argv[1]
    isValidUrl = str(url).find(CSDN_BLOG_STR) != -1
    if not isValidUrl:
        print("the first param must be a csdn blog url which must contains " + CSDN_BLOG_STR)
        exit(0)
    filePath = sys.argv[2]
    file = open(filePath, 'a', encoding="utf-8")


if __name__ == '__main__':
    checkParamAndOpenFile()
    doTranslate()
