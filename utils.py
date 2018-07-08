import re
import sys

CSDN_BLOG_STR = str("blog.csdn.net")
PARAM_LENGTH = 3


class Writer:
    """输出写入类"""
    file = None
    char_encode_array = [('<', '&lt;'), ('>', '&gt;'), ('*', 'x')]

    def __init__(self, path):
        self.file = open(path, 'w', encoding='utf-8')

    def write(self, string, html_char_encode=True):
        """写入字符串"""
        if html_char_encode:
            string = self.html_char_encode(string)
        self.file.write(string)
        pass

    def write_ignore_new_line(self, string, html_char_encode=True):
        """写入字符串，并忽略空行"""
        if html_char_encode:
            string = self.html_char_encode(string)
        string = string.replace('\n', '')
        self.file.write(string)

    def html_char_encode(self, string):
        for (html_char, encode_char) in self.__class__.char_encode_array:
            string = string.replace(html_char, encode_char)
        return string

    def new_line(self):
        """写入空行"""
        self.file.write('\n')

    def tab(self):
        """写入tab键"""
        self.file.write('   ')


def check_params():
    # check param length
    length = len(sys.argv)
    if length != PARAM_LENGTH:
        print("usage : python csdnBlogTranslator.py output_file_path csdn_url")
        exit(0)

    # check param
    out_file_path = sys.argv[1]
    url = sys.argv[2]
    is_valid_url = str(url).find(CSDN_BLOG_STR) != -1
    if not is_valid_url:
        print("the second param must be a csdn blog url which must contains " + CSDN_BLOG_STR)
        exit(0)
    return url, out_file_path


def get_blog_title(soup):
    title = soup.find_all('h1', 'title-article')[0].string
    return title


def get_blog_time(soup):
    time = soup.find_all('span', 'time')[0].string
    pattern = re.compile(r'(\d{4}).?(\d{2}).?(\d{2}).*(\d{2}).?(\d{2}).?(\d{2})')
    match = pattern.match(time)
    return "{}-{}-{} {}:{}:{}".format(match.group(1), match.group(2), match.group(3), match.group(4),
                                      match.group(5), match.group(6))


def write_blog_header(soup, writer):
    writer.write("""---
title: {}
tags: []
categories: []
date: {}
description: 
---""".format(get_blog_title(soup), get_blog_time(soup)))


def get_writer(path):
    return Writer(path)


def get_tag_all_contents_str(tag):
    result = ""
    for content in tag.contents:
        if content.string is not None:
            result += content.string
    return result
