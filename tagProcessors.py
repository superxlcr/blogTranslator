import utils


class BaseTagProcessor(object):
    """基类tag处理器"""

    def __init__(self):
        self.root_processor = None
        self.next_processor = None
        self.writer = None

    def start_process(self, tag):
        """开始处理tag"""
        for child_tag in tag.contents:
            self.root_processor.check(child_tag)

    def check(self, tag):
        """检查能否处理tag，不能则交给下游处理器"""
        if self.can_handle_tag(tag):
            self.handle(tag)
        elif self.next_processor is not None:
            self.next_processor.check(tag)
        else:
            print("{} can not be handle by any processor, is it ok ?".format(tag.name), end='\n')

    def can_handle_tag(self, tag):
        """子类实现，能否处理该tag"""
        return False

    def handle(self, tag):
        """子类实现，处理tag"""
        pass


class NavigableStringTagProcessor(BaseTagProcessor):
    """纯字符 tag 处理器"""

    miss_new_line = False

    def can_handle_tag(self, tag):
        return type(tag).__name__ == 'NavigableString'

    def handle(self, tag):
        if self.__class__.miss_new_line:
            self.writer.write_ignore_new_line(tag.string)
        else:
            self.writer.write(tag.string)


class UlTagProcessor(BaseTagProcessor):
    """<ul> tag 处理器"""

    def can_handle_tag(self, tag):
        return tag.name == 'ul'

    def handle(self, tag):
        ul_mode, ol_mode, ol_counter = LiTagProcessor.save_state()
        LiTagProcessor.begin_ul_mode()
        self.start_process(tag)
        self.writer.new_line()
        LiTagProcessor.end_mode()
        LiTagProcessor.reset_state(ul_mode, ol_mode, ol_counter)


class OlTagProcessor(BaseTagProcessor):
    """<ol> tag 处理器"""

    def can_handle_tag(self, tag):
        return tag.name == 'ol'

    def handle(self, tag):
        ul_mode, ol_mode, ol_counter = LiTagProcessor.save_state()
        LiTagProcessor.begin_ol_mode()
        self.start_process(tag)
        self.writer.new_line()
        LiTagProcessor.end_mode()
        LiTagProcessor.reset_state(ul_mode, ol_mode, ol_counter)


class LiTagProcessor(BaseTagProcessor):
    """<li> tag 处理器"""

    ul_mode = False
    ol_mode = False
    ol_counter = 1
    recursive_counter = -1

    @classmethod
    def begin_ul_mode(cls):
        cls.ul_mode = True
        cls.recursive_counter += 1

    @classmethod
    def begin_ol_mode(cls):
        cls.ol_mode = True
        cls.ol_counter = 1
        cls.recursive_counter += 1

    @classmethod
    def end_mode(cls):
        cls.recursive_counter -= 1

    @classmethod
    def save_state(cls):
        return cls.ul_mode, cls.ol_mode, cls.ol_counter

    @classmethod
    def reset_state(cls, ul_mode: bool, ol_mode: bool, ol_counter: int):
        cls.ul_mode = ul_mode
        cls.ol_mode = ol_mode
        cls.ol_counter = ol_counter

    def can_handle_tag(self, tag):
        return tag.name == 'li'

    def handle(self, tag):
        # 处理嵌套情况
        if self.__class__.recursive_counter > 0:
            for i in range(0, self.__class__.recursive_counter):
                self.writer.tab()
        if self.__class__.ul_mode:
            self.writer.write("- ")
        elif self.__class__.ol_mode:
            self.writer.write(str(self.__class__.ol_counter) + ". ")
            self.__class__.ol_counter += 1
        # 自己处理换行
        NavigableStringTagProcessor.miss_new_line = True
        BrTagProcessor.miss_br = True
        self.start_process(tag)
        self.writer.new_line()
        NavigableStringTagProcessor.miss_new_line = False
        BrTagProcessor.miss_br = False


class HTagProcessor(BaseTagProcessor):
    """<h> 标题类 tag 处理器"""

    def can_handle_tag(self, tag):
        return tag.name == 'h1' or tag.name == 'h2' or tag.name == 'h3' or tag.name == 'h4'

    def handle(self, tag):
        if tag.name == 'h1':
            self.writer.write("# ")
        elif tag.name == 'h2':
            self.writer.write("## ")
        elif tag.name == 'h3':
            self.writer.write("### ")
        elif tag.name == 'h4':
            self.writer.write("#### ")
        self.writer.write_ignore_new_line(utils.get_tag_all_contents_str(tag))


class ImgTagProcessor(BaseTagProcessor):
    """<img> tag 处理器"""

    img_counter = 0

    def can_handle_tag(self, tag):
        return tag.name == 'img'

    def handle(self, tag):
        self.__class__.img_counter += 1
        alt = tag.get('alt') if tag.get('alt') is not None else ''
        src = tag.get('src') if tag.get('src') is not None else ''
        self.writer.write("![{}_pic{}]({})".format(alt, self.__class__.img_counter, src))


class TableTagProcessor(BaseTagProcessor):
    """<table> tag 处理器"""

    def can_handle_tag(self, tag):
        return tag.name == 'table'

    def handle(self, tag):
        TrTagProcessor.table_row = 0
        TdThTagProcessor.table_column = 0
        self.start_process(tag)


class TrTagProcessor(BaseTagProcessor):
    """<tr> tag 处理器"""

    table_row = 0

    def can_handle_tag(self, tag):
        return tag.name == 'tr'

    def handle(self, tag):
        if self.__class__.table_row == 1:
            self.writer.write("|")
            for i in range(0, TdThTagProcessor.table_column):
                self.writer.write(" - |")
            self.writer.new_line()

        TdThTagProcessor.table_column = 0
        self.__class__.table_row += 1

        self.writer.write("| ")
        # 下面把换行屏蔽，由TrTag处理器统一换行
        NavigableStringTagProcessor.miss_new_line = True
        BrTagProcessor.miss_br = True
        self.start_process(tag)
        self.writer.new_line()
        NavigableStringTagProcessor.miss_new_line = False
        BrTagProcessor.miss_br = False


class TdThTagProcessor(BaseTagProcessor):
    """<td> <th> tag 处理器"""

    table_column = 0

    def can_handle_tag(self, tag):
        return tag.name == 'td' or tag.name == 'th'

    def handle(self, tag):
        self.__class__.table_column += 1
        self.start_process(tag)
        self.writer.write(" | ")


class NestingTagProcessor(BaseTagProcessor):
    """嵌套 tag 处理器"""

    def can_handle_tag(self, tag):
        return len(tag.contents) > 1 or len(tag.contents) == 1 and type(tag.contents[0]).__name__ != 'NavigableString'

    def handle(self, tag):
        if tag.name == 'a' or tag.name == 'strong':
            print('the tag is <{}>, may be handle by nesting is wrong'.format(tag.name), end='\n')
        self.start_process(tag)


class ATagProcessor(BaseTagProcessor):
    """<a> tag 处理器"""

    def can_handle_tag(self, tag):
        return tag.name == 'a'

    def handle(self, tag):
        content = tag.string
        href = tag.get('href') if tag.get('href') is not None else ''
        if content == href:
            self.writer.write(content)
        else:
            self.writer.write("[{}]({})".format(content, href))


class BrTagProcessor(BaseTagProcessor):
    """<br> tag 处理器"""

    miss_br = False

    def can_handle_tag(self, tag):
        return tag.name == 'br'

    def handle(self, tag):
        if not self.__class__.miss_br:
            self.writer.new_line()


class CodeTagProcessor(BaseTagProcessor):
    """<code> tag 处理器"""

    def can_handle_tag(self, tag):
        return tag.name == 'code'

    def handle(self, tag):
        self.writer.new_line()
        self.writer.write("```" + self.get_code_type(tag.get('class')))
        self.writer.new_line()
        self.writer.write(utils.get_tag_all_contents_str(tag), html_char_encode=False)
        self.writer.new_line()
        self.writer.write("```")
        self.writer.new_line()

    def get_code_type(self, str_array):
        if str_array is not None:
            for string in str_array:
                if string.find('java') != -1:
                    return 'java'
                elif string.find('html') != -1:
                    return 'html'
                elif string.find('bash') != -1:
                    return 'bash'
                elif string.find('cpp') != -1:
                    return 'cpp'
        return ''


class NormalTextTagProcessor(BaseTagProcessor):
    """普通文本 tag 处理器，如 <p> <div>"""

    def can_handle_tag(self, tag):
        return tag.name == 'p' or tag.name == 'div' or tag.name == 'span'

    def handle(self, tag):
        if tag.string is not None:
            self.writer.write(tag.string)


class StrongTagProcessor(BaseTagProcessor):
    """<strong> tag 处理器"""

    def can_handle_tag(self, tag):
        return tag.name == 'strong'

    def handle(self, tag):
        self.writer.write_ignore_new_line("**{}**".format(tag.string))
