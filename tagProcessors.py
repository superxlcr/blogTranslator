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

    @classmethod
    def set_miss_new_line(cls, value: bool):
        cls.miss_new_line = value

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
        LiTagProcessor.ul_mode = True
        self.start_process(tag)


class LiTagProcessor(BaseTagProcessor):
    """<li> tag 处理器"""

    ul_mode = False
    ol_mode = False

    def can_handle_tag(self, tag):
        return tag.name == 'li'

    def handle(self, tag):
        if self.ul_mode:
            self.writer.write("- ")
        self.start_process(tag)


class HTagProcessor(BaseTagProcessor):
    """<h> 标题类 tag 处理器"""

    def can_handle_tag(self, tag):
        return tag.name == 'h1' or tag.name == 'h2'

    def handle(self, tag):
        if tag.name == 'h1':
            self.writer.write("# ")
        elif tag.name == 'h2':
            self.writer.write("## ")
        self.writer.write_ignore_new_line(utils.get_tag_all_contents_str(tag))


class ImgTagProcessor(BaseTagProcessor):
    """<img> tag 处理器"""

    img_counter = 0

    def can_handle_tag(self, tag):
        return tag.name == 'img'

    def handle(self, tag):
        self.img_counter += 1
        self.writer.write("![{}_pic{}]({})".format(tag['alt'], self.img_counter, tag['src']))


class TBodyTagProcessor(BaseTagProcessor):
    """<tbody> tag 处理器"""

    def can_handle_tag(self, tag):
        return tag.name == 'tbody'

    def handle(self, tag):
        TrTagProcessor.clear_table_row()
        TdTagProcessor.clear_table_column()
        self.start_process(tag)


class TrTagProcessor(BaseTagProcessor):
    """<tr> tag 处理器"""

    table_row = 0

    @classmethod
    def clear_table_row(cls):
        cls.table_row = 0

    def can_handle_tag(self, tag):
        return tag.name == 'tr'

    def handle(self, tag):
        if self.table_row == 1:
            self.writer.write("|")
            for i in range(0, TdTagProcessor.get_table_column()):
                self.writer.write(" - |")
            self.writer.new_line()

        TdTagProcessor.clear_table_column()
        self.__class__.table_row += 1

        self.writer.write("| ")
        # 下面把换行屏蔽，由TrTag处理器统一换行
        NavigableStringTagProcessor.set_miss_new_line(True)
        BrTagProcessor.set_miss_br(True)
        self.start_process(tag)
        self.writer.new_line()
        NavigableStringTagProcessor.set_miss_new_line(False)
        BrTagProcessor.set_miss_br(False)


class TdTagProcessor(BaseTagProcessor):
    """<td> tag 处理器"""

    table_column = 0

    @classmethod
    def clear_table_column(cls):
        cls.table_column = 0

    @classmethod
    def get_table_column(cls):
        return cls.table_column

    def can_handle_tag(self, tag):
        return tag.name == 'td'

    def handle(self, tag):
        self.__class__.table_column += 1
        self.start_process(tag)
        self.writer.write(" | ")


class NestingTagProcessor(BaseTagProcessor):
    """嵌套 tag 处理器"""

    def can_handle_tag(self, tag):
        return len(tag.contents) > 1 or len(tag.contents) == 1 and type(tag.contents[0]).__name__ != 'NavigableString'

    def handle(self, tag):
        self.start_process(tag)


class ATagProcessor(BaseTagProcessor):
    """<a> tag 处理器"""

    def can_handle_tag(self, tag):
        return tag.name == 'a'

    def handle(self, tag):
        content = tag.string
        href = tag['href']
        if content == href:
            self.writer.write(content)
        else:
            self.writer.write("[{}]({})".format(content, href))


class BrTagProcessor(BaseTagProcessor):
    """<br> tag 处理器"""

    miss_br = False

    @classmethod
    def set_miss_br(cls, value: bool):
        cls.miss_br = value

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
        # TODO 识别语言类型
        self.writer.write("```")
        self.writer.new_line()
        self.writer.write(tag.string)
        self.writer.new_line()
        self.writer.write("\n```")


class NormalTextTagProcessor(BaseTagProcessor):
    """普通文本 tag 处理器，如 <p> <div>"""

    def can_handle_tag(self, tag):
        return tag.name == 'p' or tag.name == 'div'

    def handle(self, tag):
        if tag.string is not None:
            self.writer.write(tag.string)


class StrongTagProcessor(BaseTagProcessor):
    """<strong> tag 处理器"""

    def can_handle_tag(self, tag):
        return tag.name == 'strong'

    def handle(self, tag):
        self.writer.write_ignore_new_line("**{}**".format(tag.string))
