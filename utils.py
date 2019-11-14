import re
import sys
import time as time_lib

from enumUtils import BlogType
from writer import Writer

PARAM_LENGTH = 3
JIANSHU_ROOT_TAG_NAME = ["show-content-free", "_2rhmJa"]


def check_params():
    # check param length
    length = len(sys.argv)
    if length != PARAM_LENGTH:
        print("usage : python blogTranslator.py output_dir blog_url")
        exit(0)

    # check param
    out_dir = sys.argv[1]
    url = sys.argv[2]
    blog_type = BlogType.unknown
    if str(url).find(BlogType.csdn.value) != -1:
        blog_type = BlogType.csdn
    elif str(url).find(BlogType.jianshu.value) != -1:
        blog_type = BlogType.jianshu
    else:
        print("the second param must be a csdn or jianshu blog url which must contains\n {}\n or\n {}".format(
            BlogType.csdn.value, BlogType.jianshu.value))
        exit(0)
    return url, out_dir, blog_type


def get_blog_title(soup, blog_type: BlogType):
    title = ""
    if blog_type == BlogType.csdn:
        title = soup.find_all('h1', 'title-article')[0].string
    elif blog_type == BlogType.jianshu:
        if len(soup.find_all('h1', 'title')) != 0:
            title = soup.find_all('h1', 'title')[0].string
        elif len(soup.find_all('h1')) != 0:
            title = soup.find_all('h1')[0].string
        else:
            title = "未知标题"
    return title


def get_blog_time(soup, blog_type: BlogType):
    time_str = ""
    if blog_type == BlogType.csdn and len(soup.find_all('span', 'time')) != 0:
        time = soup.find_all('span', 'time')[0].string
        pattern = re.compile(r'(\d{4}).?(\d{2}).?(\d{2}).*(\d{2}).?(\d{2}).?(\d{2})')
        match = pattern.match(time)
        time_str = "{}-{}-{} {}:{}:{}".format(match.group(1), match.group(2), match.group(3), match.group(4),
                                              match.group(5), match.group(6))
    elif blog_type == BlogType.jianshu and len(soup.find_all('span', 'publish-time')) != 0:
        time = soup.find_all('span', 'publish-time')[0].string
        pattern = re.compile(r'(\d{4}).?(\d{2}).?(\d{2}).*(\d{2}).?(\d{2})')
        match = pattern.match(time)
        time_str = "{}-{}-{} {}:{}:00".format(match.group(1), match.group(2), match.group(3), match.group(4),
                                              match.group(5))
    if len(time_str) == 0:
        # 如果获取时间失败，则用当前时间代替
        time_str = time_lib.strftime("%Y-%m-%d %H:%M:%S", time_lib.localtime())
    return time_str


def write_blog_header(soup, writer, blog_type: BlogType):
    writer.write("""---
title: {}
tags: []
categories: []
date: {}
description: 
---""".format(get_blog_title(soup, blog_type), get_blog_time(soup, blog_type)))


def get_root_tag(soup, blog_type: BlogType):
    root_tag = None
    if blog_type == BlogType.csdn:
        root_tag = soup.find_all('div', 'htmledit_views')
        if len(root_tag) == 0:
            root_tag = soup.find_all('div', 'markdown_views')
    elif blog_type == BlogType.jianshu:
        root_tag = get_jianshu_root_tag(soup)
    if root_tag is not None:
        root_tag = root_tag[len(root_tag) - 1]
    return root_tag


def get_jianshu_root_tag(soup):
    for name in JIANSHU_ROOT_TAG_NAME:
        if len(soup.find_all('div', name)) != 0:
            return soup.find_all('div', name)
    return None


def get_writer(dir_path, blog_type: BlogType):
    return Writer(dir_path, blog_type)


def get_tag_all_contents_str(tag):
    result = ""
    if type(tag).__name__ == 'NavigableString' or len(tag.contents) == 0:
        if tag.string is not None:
            result += tag.string
    else:
        for content in tag.contents:
            result += get_tag_all_contents_str(content)
    return result


def get_valid_url(url):
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return "http://" + url.lstrip('/')
