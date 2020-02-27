'''
定义上下文无关文法（CFG）
'''
EPS = ('_EPS', '_EPS')

START_SYMBOL = 'STMT'

GRAMMARS = {
    'STMT': {
        'expr_stmt': (('N', 'E'), ('T', ';'), ('N', 'STMT')),
        'print_stmt': (('T', 'PRINT'), ('T', '('), ('N', 'E'), ('T', ')'), ('T', ';'), ('N', 'STMT')),
        'if_stmt': (('T', 'IF'), ('N', 'E'), ('T', '{'), ('N', 'STMT'), ('T', '}'), ('N', 'ELSE'), ('N', 'STMT')),
        'loop_stmt': (('T', 'LOOP'), ('T', 'ID'), ('T', 'FROM'), ('N', 'E'), ('T', 'TO'), ('N', 'E'), ('T', '{'), ('N', 'STMT'), ('T', '}'), ('N', 'STMT')),
        'while_stmt': (('T', 'WHILE'), ('N', 'E'), ('T', '{'), ('N', 'STMT'), ('T', '}'), ('N', 'STMT')),
        'func_stmt': (('T', 'FUNC'), ('T', 'ID'), ('T', '('), ('N', 'VPARAM_LIST'), ('T', ')'), ('T', '{'), ('N', 'STMT'), ('T', '}'), ('N', 'STMT')),
        'ret_stmt': (('T', 'RET'), ('N', 'E'), ('T', ';'), ('N', 'STMT')),
        'assign_stmt': (('T', 'LET'), ('T', 'ID'), ('N', 'ARRSUF'), ('T', 'EQ'), ('N', 'E'), ('T', ';'), ('N', 'STMT')),
        'eps': (EPS, ),
    },
    'VPARAM_LIST': {
        'list': (('T', 'ID'), ('N', 'VPARAM_LIST_EXTRA')),
        'eps': (EPS, )
    },
    'VPARAM_LIST_EXTRA': {
        'list': (('T', ','), ('T', 'ID'), ('N', 'VPARAM_LIST_EXTRA')),
        'eps': (EPS, )
    },
    'RPARAM_LIST': {
        'list': (('N', 'E'), ('N', 'RPARAM_LIST_EXTRA')),
        'eps': (EPS, )
    },
    'RPARAM_LIST_EXTRA': {
        'list': (('T', ','), ('N', 'E'), ('N', 'RPARAM_LIST_EXTRA')),
        'eps': (EPS, )
    },
    'ELSE': {
        'else': (('T', 'ELSE'), ('T', '{'), ('N', 'STMT'), ('T', '}')),
        'eps': (EPS, )
    },
    'E': {
        'suffix': (('N', 'LOGIC_CALC_VAL'), )
    },
    'LOGIC_CALC_VAL': {
        'suffix': (('N', 'CMP_CALC_VAL'), ('N', 'LOGIC_CALC'))
    },
    'LOGIC_CALC': {
        'land_expr': (('T', 'ANDL'), ('N', 'CMP_CALC_VAL'), ('N', 'LOGIC_CALC')),
        'lor_expr': (('T', 'ORL'), ('N', 'CMP_CALC_VAL'), ('N', 'LOGIC_CALC')),
        'eps': (EPS, )
    },
    'CMP_CALC_VAL': {
        'suffix': (('N', 'SUM'), ('N', 'CMP_CALC'))
    },
    'CMP_CALC': {
        'lt': (('T', 'LT'), ('N', 'SUM'), ('N', 'CMP_CALC')),
        'gt': (('T', 'GT'), ('N', 'SUM'), ('N', 'CMP_CALC')),
        'lte': (('T', 'LTE'), ('N', 'SUM'), ('N', 'CMP_CALC')),
        'gte': (('T', 'GTE'), ('N', 'SUM'), ('N', 'CMP_CALC')),
        'eq': (('T', 'IS_EQ'), ('N', 'SUM'), ('N', 'CMP_CALC')),
        'neq': (('T', 'NEQ'), ('N', 'SUM'), ('N', 'CMP_CALC')),
        'eps': (EPS, )
    },
    'SUM': {
        'suffix': (('N', 'T'), ('N', 'X'))
    },
    'X': {
        'plus_expr': (('T', 'PLUS'), ('N', 'T'), ('N', 'X')),
        'sub_expr': (('T', 'SUB'), ('N', 'T'), ('N', 'X')),
        'eps': (EPS, )
    },
    'T': {
        'suffix': (('N', 'F'), ('N', 'Y')),
        'string': (('T', 'STRING_LITERAL'), ),
    },
    'Y': {
        'prod_expr': (('T', 'PROD'), ('N', 'F'), ('N', 'Y')),
        'div_expr': (('T', 'DIV'), ('N', 'F'), ('N', 'Y')),
        'mod_expr': (('T', '%'), ('N', 'F'), ('N', 'Y')),
        'eps': (EPS, )
    },
    'ARRSUF': {
        'arr': (('T', '['), ('N', 'E'), ('T', ']'), ('N', 'ARRSUF')),
        'eps': (EPS, )
    },
    'IDSUF': {
        'eps': (EPS, ),
        'func': (('T', '('), ('N', 'RPARAM_LIST'), ('T', ')')),
        'arr': (('T', '['), ('N', 'E'), ('T', ']'), ('N', 'ARRSUF'))
    },
    'F': {
        'number': (('T', 'NUMBER_LITERAL'), ),
        'negative_number': (('T', 'SUB'), ('N', 'F'), ),
        'id_head': (('T', 'ID'), ('N', 'IDSUF')),
        'not': (('T', 'NOT'), ('N', 'F')),
        'int': (('T', 'INT'), ('T', '('), ('N', 'E'), ('T', ')')),
        'brackets': (('T', '('), ('N', 'E'), ('T', ')')),
        'array_init': (('T', 'ARRAY'), )
    }
}