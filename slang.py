from src_code import SourceCode
import sys
import importlib

if __name__ == '__main__':
    path = sys.argv[1]
    SourceCode.set_source_path(path)
    sdd = importlib.import_module('simple_sdd')
    parsing_predict = importlib.import_module('parsing_predict')
    parsing_predict.ParseTree.build_parse_tree()
    parse_tree = parsing_predict.ParseTree.get_parse_tree()
    sdd.simple_sdd(parse_tree)
