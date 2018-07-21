import os
import re
import sys
from urllib import request

CSDN_BLOG_STR = str("blog.csdn.net")
PARAM_LENGTH = 3
BLOG_FILE_NAME = "blog"


class Writer:
    """输出写入类"""
    dir_path = None
    file = None
    CHAR_ENCODE_LIST = [('<', '&lt;'), ('>', '&gt;'), ('*', 'x')]
    IMAGE_SUFFIX_LIST = {('png', '.png'), ('jpeg', '.jpg'), ('gif', '.gif')}

    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.file = open(os.path.join(dir_path, BLOG_FILE_NAME), 'w', encoding='utf-8')

    def write(self, string, html_char_encode=True):
        """写入字符串"""
        if string is None:
            return
        if html_char_encode:
            string = self.html_char_encode(string)
        self.file.write(string)
        pass

    def write_ignore_new_line(self, string, html_char_encode=True):
        """写入字符串，并忽略空行"""
        if string is None:
            return
        if html_char_encode:
            string = self.html_char_encode(string)
        string = string.replace('\n', '')
        self.file.write(string)

    def html_char_encode(self, string):
        for (html_char, encode_char) in self.__class__.CHAR_ENCODE_LIST:
            string = string.replace(html_char, encode_char)
        return string

    def new_line(self):
        """写入空行"""
        self.file.write('\n')

    def tab(self):
        """写入tab键"""
        self.file.write('   ')

    def download_image(self, image_url, file_name):
        req = request.Request(image_url)
        req.add_header("referer", "https://blog.csdn.net")
        response = request.urlopen(req)
        content_type = response.getheader('Content-Type')
        image_suffix = ""
        for key, suffix in self.__class__.IMAGE_SUFFIX_LIST:
            if content_type.find(key) != -1:
                image_suffix = suffix
                break
        image = response.read()
        file_name_with_suffix = str(file_name) + image_suffix
        file = open(os.path.join(self.dir_path, file_name_with_suffix), 'wb')
        file.write(image)
        return file_name_with_suffix


def check_params():
    # check param length
    length = len(sys.argv)
    if length != PARAM_LENGTH:
        print("usage : python csdnBlogTranslator.py output_dir csdn_url")
        exit(0)

    # check param
    out_dir = sys.argv[1]
    url = sys.argv[2]
    is_valid_url = str(url).find(CSDN_BLOG_STR) != -1
    if not is_valid_url:
        print("the second param must be a csdn blog url which must contains " + CSDN_BLOG_STR)
        exit(0)
    return url, out_dir


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


def get_writer(dir_path):
    return Writer(dir_path)


def get_tag_all_contents_str(tag):
    result = ""
    if type(tag).__name__ == 'NavigableString' or len(tag.contents) == 0:
        if tag.string is not None:
            result += tag.string
    else:
        for content in tag.contents:
            result += get_tag_all_contents_str(content)
    return result
