import re
import sys

CSDN_BLOG_STR = str("blog.csdn.net")
PARAM_LENGTH = 3


def check_params():
    # check param length
    length = len(sys.argv)
    if length != PARAM_LENGTH:
        print("usage : python csdnBlogTranslator.py csdn_url output_file_path")
        exit(0)

    # check param
    url = sys.argv[1]
    is_valid_url = str(url).find(CSDN_BLOG_STR) != -1
    if not is_valid_url:
        print("the first param must be a csdn blog url which must contains " + CSDN_BLOG_STR)
        exit(0)
    out_file_path = sys.argv[2]
    return url, out_file_path


def write_title(soup, writer):
    title = soup.find_all('h1', 'title-article')[0].string
    writer.write("title : " + title)
    writer.new_line()


def write_time(soup, writer):
    time = soup.find_all('span', 'time')[0].string
    pattern = re.compile(r'(\d{4}).?(\d{2}).?(\d{2}).*(\d{2}).?(\d{2}).?(\d{2})')
    match = pattern.match(time)
    writer.write("time : {}-{}-{} {}:{}:{}\n\n".format(match.group(1), match.group(2), match.group(3),
                                                       match.group(4), match.group(5), match.group(6)))


class Writer:
    """输出写入类"""
    file = None

    def __init__(self, path):
        self.file = open(path, 'w', encoding='utf-8')

    def write(self, string):
        """写入字符串"""
        self.file.write(string)
        pass

    def write_without_new_line(self, string):
        """写入字符串，并忽略空行"""
        string = string.replace('\n', '')
        self.file.write(string)

    def new_line(self):
        """写入空行"""
        self.file.write('\n')


def get_writer(path):
    return Writer(path)
