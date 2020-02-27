from lexing import TokenStream, EOF
from parse_tree import ParseTree_Node
from grammars import GRAMMARS, START_SYMBOL, EPS
from grammar_helper import GrammarHelper
from prettytable import PrettyTable
import sys
from copy import deepcopy

PARSETREE_ROOT_START_SYMBOL = 'S'

def panic(msg):
    # PredictTableGenerator.print_first()
    # PredictTableGenerator.print_follow()
    print('Syntax error: {}'.format(msg))
    print('Parser failed, exiting...')
    sys.exit()

class PredictTableGenerator:
    _FIRST = {}
    _FOLLOW = {}
    _PARSE_TABLE = {}

    # right hand side FIRST
    @staticmethod
    def _get_first_rhs(production):
        rhs_first = set()
        no_eps = False

        for element in production:
            node_first = PredictTableGenerator._get_first(element)
            rhs_first |= (node_first - {EPS})
            if EPS not in node_first:
                no_eps = True
                break
        if not no_eps:
            rhs_first.add(EPS)

        return rhs_first
    
    # left hand side FIRST
    @staticmethod
    def _get_first(element):
        if element in PredictTableGenerator._FIRST:
            return PredictTableGenerator._FIRST[element]

        node_type, name = element
        if element == EPS or node_type == 'T':
            PredictTableGenerator._FIRST[element] = {element}
            return {element}
        
        first = PredictTableGenerator._FIRST[element] = set()
        for (name, production) in GRAMMARS[element[1]].items():
            first |= PredictTableGenerator._get_first_rhs(production)
        
        return first
    
    # calculate first table
    @staticmethod
    def calc_first():
        for element in GrammarHelper.ALL:
            PredictTableGenerator._get_first(element)

    # FOLLOW, must use iteration here
    @staticmethod
    def calc_follow():
        last_follow = {}
        for element in GrammarHelper.N:
            last_follow[element] = set()
            if element[1] == START_SYMBOL:
                last_follow[element].add(EOF)
        
        while True:
            follow = deepcopy(last_follow)

            for element in GrammarHelper.N:
                for (lhs, (name, production), follow_el) in GrammarHelper.get_productions_with(element):
                    first = set()
                    # condition 1
                    if follow_el is not None:
                        first = PredictTableGenerator._FIRST[follow_el]
                        # print('merge first {}::=={} follow={} {} to {}'.format(lhs, name, follow_el, first - {EPS}, element))
                        follow[element] |= first - {EPS}
                    # condition 2
                    if (follow_el is None or EPS in first) and (lhs != element): # very important: (lhs != element)
                        # print('merge follow {}::=={} {} to {}'.format(lhs, name, last_follow[lhs], element))
                        follow[element] |= last_follow[lhs]
            
            if follow == last_follow:
                PredictTableGenerator._FOLLOW = follow
                return
            
            last_follow = follow
            del follow

    # print FOLLOW set
    @staticmethod
    def print_follow():
        for element in GrammarHelper.N:
            print('FOLLOW[{}]={}'.format(element, PredictTableGenerator._FOLLOW[element]))
    
    # print FIRST set
    @staticmethod
    def print_first():
        for element in GrammarHelper.ALL:
            print('FIRST[{}]={}'.format(element, PredictTableGenerator._FIRST[element]))

    # get parse table
    @staticmethod
    def get_parse_table():
        if len(PredictTableGenerator._PARSE_TABLE):
            return PredictTableGenerator._PARSE_TABLE

        PredictTableGenerator._PARSE_TABLE = {}
        parse_table = PredictTableGenerator._PARSE_TABLE
        for (lhs, (name, rhs)) in GrammarHelper.P:
            first = PredictTableGenerator._get_first_rhs(rhs)
            for look_ahead_terminal in (first - {EPS}):
                if (lhs, look_ahead_terminal) in parse_table:
                    panic('No EPS in first: Parse table construction failure: {} {} is already in parse table with value {}, but attempting to add [{}]{}'.format(lhs, look_ahead_terminal, parse_table[lhs, look_ahead_terminal], name, rhs))
                parse_table[lhs, look_ahead_terminal] = (name, rhs)
            if EPS in first:
                for look_ahead_terminal in PredictTableGenerator._FOLLOW[lhs]:
                    if (lhs, look_ahead_terminal) in parse_table:
                        panic('EPS in first: Parse table construction failure: {} {} is already in parse table with value {}, but attempting to add [{}]{}'.format(lhs, look_ahead_terminal, parse_table[lhs, look_ahead_terminal], name, rhs))
                    parse_table[lhs, look_ahead_terminal] = (name, rhs)
        
        return parse_table
    
    # print parse table
    @staticmethod
    def print_parse_table():
        parse_table = PredictTableGenerator.get_parse_table()
        tbl = PrettyTable(['-'] + [x[1] for x in (GrammarHelper.T | {EOF})])
        for non_terminal in GrammarHelper.N:
            row = [non_terminal[1]]
            for col in (GrammarHelper.T | {EOF}):
                if (non_terminal, col) not in parse_table:
                    row.append('-')
                else:
                    row.append(parse_table[non_terminal, col])
            tbl.add_row(row)
        print(tbl)

PredictTableGenerator.calc_first()
PredictTableGenerator.calc_follow()

class ParseTree:
    _parse_stack = []
    _parse_tree_root_node = None

    @staticmethod
    def get_parse_tree():
        return ParseTree._parse_tree_root_node

    @staticmethod
    def build_parse_tree():
        parse_stack = ParseTree._parse_stack
        ParseTree._parse_tree_root_node = ParseTree_Node('N', symbol=PARSETREE_ROOT_START_SYMBOL, production_name=PARSETREE_ROOT_START_SYMBOL)
        parse_stack.append((('N', START_SYMBOL), ParseTree._parse_tree_root_node))
        parse_table = PredictTableGenerator.get_parse_table()
        while len(parse_stack):
            # 这里不能直接next，因为如果当前top为非终结符号，则不应该往后读取，这就是设定“向前看”专用函数的原因
            look_ahead = TokenStream.get_look_ahead()
            element, cur_node = parse_stack[-1]

            if element[0] == 'T':
                token = TokenStream.next()
                if token[0] != element[1]:
                    panic('Unexpected token: {}, expected: {}.'.format(token[0], element[1]))
                cur_node.add_child(ParseTree_Node('T', token=token))
                parse_stack.pop()
                continue
            elif element[0] == '_EPS':
                cur_node.add_child(ParseTree_Node('_EPS'))
                parse_stack.pop()
                continue
            # 否则就是非终结符

            # 选择合适的产生式
            try:
                look_ahead_name = ('T', look_ahead[0]) if look_ahead != EOF else EOF
                name, production = parse_table[element, look_ahead_name]
            except KeyError:
                panic('Unexpected token: {}.'.format(look_ahead[0]))
            
            # 增加子节点
            child = ParseTree_Node('N', symbol=element[1], production_name=name)
            cur_node.add_child(child)
            
            # 弹栈
            parse_stack.pop()
            for component in reversed(production): # 注意逆序加入，因为最左推导原则
                parse_stack.append((component, child))

        if not TokenStream.is_finished():
            remain_tokens = []
            while not TokenStream.is_finished():
                remain_tokens.append(str(TokenStream.next()))
            
            panic('Unexpected token {} at the end of the file.'.format(', '.join(remain_tokens)))
        
        if len(parse_stack):
            parse_stack_elements = [str(x[0]) for x in parse_stack]
            panic('Parse stack is not empty, remaining "{}".'.format(', '.join(parse_stack_elements)))

# for testing
if __name__ == '__main__':
    # PredictTableGenerator.print_first()
    # PredictTableGenerator.print_follow()
    # PredictTableGenerator.print_parse_table()
    ParseTree.build_parse_tree()
    # ParseTree.get_parse_tree().print_tree()