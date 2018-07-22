import os
from urllib import request

BLOG_FILE_NAME = "blog"


class Writer:
    """输出写入类"""
    # &emsp;
    CHAR_FORCE_IGNORE_LIST = [' ']
    CHAR_HTML_ENCODE_LIST = [('<', '&lt;'), ('>', '&gt;'), ('*', 'x')]
    IMAGE_SUFFIX_LIST = {('png', '.png'), ('jpeg', '.jpg'), ('gif', '.gif')}

    dir_path = None
    file = None
    disable_new_line = False

    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.file = open(os.path.join(dir_path, BLOG_FILE_NAME), 'w', encoding='utf-8')

    def write(self, string, html_char_encode=True):
        """写入字符串"""
        if self.disable_new_line:
            # 如果开启了关闭换行flag，则使用另一个方法写入
            self.write_ignore_new_line(string, html_char_encode)
            return
        if string is None:
            return
        if html_char_encode:
            string = self.handle_html_encode_char(string)
        string = self.handle_force_ignore_char(string)
        self.file.write(string)
        pass

    def write_ignore_new_line(self, string, html_char_encode=True):
        """写入字符串，并忽略空行"""
        if string is None:
            return
        if html_char_encode:
            string = self.handle_html_encode_char(string)
        string = string.replace('\n', '')
        string = self.handle_force_ignore_char(string)
        self.file.write(string)

    def handle_html_encode_char(self, string):
        for (html_char, encode_char) in self.__class__.CHAR_HTML_ENCODE_LIST:
            string = string.replace(html_char, encode_char)
        return string

    def handle_force_ignore_char(self, string):
        for force_ignore_char in self.__class__.CHAR_FORCE_IGNORE_LIST:
            string = string.replace(force_ignore_char, '')
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
