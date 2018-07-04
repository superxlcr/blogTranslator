def build_tag_processor(writer):
    root_processor = BaseTagProcessor()
    root_processor.root_processor = root_processor
    root_processor.writer = writer

    root_processor \
        .set_next_processor(NavigableStringTagProcessor()) \
        .set_next_processor(UlTagProcessor())

    return root_processor


class BaseTagProcessor(object):
    """基类tag处理器"""

    root_processor = None
    next_processor = None
    writer = None

    def set_next_processor(self, processor):
        """设置下个处理器并返回"""
        self.next_processor = processor
        processor.root_processor = self.root_processor
        processor.writer = self.writer
        return processor

    def process(self, tag):
        """开始处理tag"""
        for child_tag in tag.contents:
            if self.can_handle_tag(child_tag):
                self.handle(child_tag)
            elif self.next_processor is not None:
                self.next_processor.process(child_tag)

    def can_handle_tag(self, tag):
        """子类实现，能否处理该tag"""
        return False

    def handle(self, tag):
        """子类实现，处理tag"""
        pass


class NavigableStringTagProcessor(BaseTagProcessor):
    """纯字符 tag 处理类"""

    def can_handle_tag(self, tag):
        return type(tag).__name__ == 'NavigableString'

    def handle(self, tag):
        # todo 忽略空格的情况？
        self.writer.write(tag.string)


class UlTagProcessor(BaseTagProcessor):
    """<ul> tag 处理类"""

    def can_handle_tag(self, tag):
        return tag.name == 'ul'

    def handle(self, tag):
        for li_tag in tag.contents:
            self.writer.write("- ")
            self.root_processor.process(li_tag)
            self.writer.new_line()
