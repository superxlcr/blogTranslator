import os
import ssl
from urllib import request

from bs4 import BeautifulSoup

import processorChainBuilder
import utils
from enumUtils import BlogType

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"


def translate(url, my_writer, blog_type: BlogType):
    # net request
    print("do request with url : " + url)
    context = ssl._create_unverified_context()
    req = request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    response = request.urlopen(req, context=context).read().decode('utf-8')
    soup = BeautifulSoup(response, 'html.parser')

    # write blog header
    utils.write_blog_header(soup, my_writer, blog_type)

    root_tag = utils.get_root_tag(soup, blog_type)
    if root_tag is None:
        print("root tag is None !")
        exit()
    root_processor = processorChainBuilder.build_tag_processor(my_writer)
    root_processor.check(root_tag)

    print("done !")


if __name__ == '__main__':
    url_param, output_dir, blog_type_param = utils.check_params()
    if not os.path.exists(output_dir) or not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    writer = utils.get_writer(output_dir, blog_type_param)
    translate(url_param, writer, blog_type_param)
