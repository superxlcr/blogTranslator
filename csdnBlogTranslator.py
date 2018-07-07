from urllib import request

from bs4 import BeautifulSoup

import processorChainBuilder
import utils


def translate(url, my_writer):
    # net request
    print("do request with url : " + url)
    response = request.urlopen(url).read().decode('utf-8')
    soup = BeautifulSoup(response, 'html.parser')

    # write blog header
    utils.write_blog_header(soup, my_writer)

    root_tag = soup.find_all('div', 'htmledit_views')
    if len(root_tag) == 0:
        root_tag = soup.find_all('div', 'markdown_views')
    root_processor = processorChainBuilder.build_tag_processor(my_writer)
    root_processor.check(root_tag[len(root_tag) - 1])

    print("done !")


if __name__ == '__main__':
    url_param, file_path = utils.check_params()
    writer = utils.get_writer(file_path)
    translate(url_param, writer)
