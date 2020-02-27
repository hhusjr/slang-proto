'''
源代码读取设置类
'''
class SourceCode:
    _path = ''

    @staticmethod
    def set_source_path(path):
        SourceCode._path = path

    @staticmethod
    def read_src_code():
        code = ''
        with open(SourceCode._path, 'r') as fd:
            code = fd.read()
        for ch in code:
            yield ch
        yield None
