from tagProcessors import *
from utils import Writer


def build_tag_processor(writer: Writer):
    return ProcessorChainBuilder(NavigableStringTagProcessor(), writer) \
        .next(UlTagProcessor()) \
        .next(OlTagProcessor()) \
        .next(LiTagProcessor()) \
        .next(HTagProcessor()) \
        .next(ImgTagProcessor()) \
        .next(TBodyTagProcessor()) \
        .next(TrTagProcessor()) \
        .next(TdTagProcessor()) \
        .next(CodeTagProcessor()) \
        .next(NestingTagProcessor()) \
        .next(ATagProcessor()) \
        .next(BrTagProcessor()) \
        .next(NormalTextTagProcessor()) \
        .next(StrongTagProcessor()) \
        .build()


class ProcessorChainBuilder:
    """处理链构造器"""

    def __init__(self, root_processor: BaseTagProcessor, writer: Writer):
        self.root_processor = root_processor
        self.processor = root_processor
        self.writer = writer

        root_processor.root_processor = root_processor
        root_processor.writer = writer

    def next(self, processor: BaseTagProcessor):
        """添加下一个处理器并返回"""
        self.processor.next_processor = processor
        self.processor = processor

        processor.root_processor = self.root_processor
        processor.writer = self.writer

        return self

    def build(self):
        return self.root_processor
