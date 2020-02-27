'''
简单的语法制导翻译器
使用了简单的一些语法制导定义的特性，所以交simple_sdd
'''

from parsing_predict import ParseTree
import sys
import uuid
from types import GeneratorType
from runtime import RuntimeFunctions

SYS_SYMBOL_PREFIX = '__' + str(uuid.uuid4()) + '__'
SDD_CALL_STACK = []

def panic(msg):
    print('Fatal error: {}'.format(msg))
    print('SDD Failed, exiting...')
    sys.exit()

class SymbolTable:
    SCOPE_STACK = [{}]

    @staticmethod
    def get(identifier):
        try:
            return SymbolTable.get_with_error(identifier)
        except KeyError:
            panic('Unknown identifier {}'.format(identifier))

    @staticmethod
    def get_with_error(identifier):
        try:
            pos = -1
            while identifier not in SymbolTable.SCOPE_STACK[pos]:
                pos -= 1
        except IndexError:
            raise KeyError
        
        return SymbolTable.SCOPE_STACK[pos][identifier]
    
    @staticmethod
    def assign(identifier, val):
        SymbolTable.SCOPE_STACK[-1][identifier] = val
        return SymbolTable.SCOPE_STACK[-1][identifier]

    @staticmethod
    def enter_scope():
        SymbolTable.SCOPE_STACK.append({})

    @staticmethod
    def leave_scope():
        SymbolTable.SCOPE_STACK.pop()

    @staticmethod
    def get_current_scope_symbols_ref():
        return SymbolTable.SCOPE_STACK[-1]

    @staticmethod
    def exists(identifier):
        try:
            pos = -1
            while identifier not in SymbolTable.SCOPE_STACK[pos]:
                pos -= 1
        except IndexError:
            return False
        
        return True

class Utils:
    '''
    辅助函数
    获取二元四则运算（五则其实是，包括mod）的结果和类型
    '''
    @staticmethod
    def binary_normal_calc(op, l, r):
        (l_val, l_type) = l
        (r_val, r_type) = r

        valid_types = ('int', 'float', 'string')
        if l_type not in valid_types or r_type not in valid_types:
            panic('Invalid {} operator between two expressions.'.format(op))
        if l_type == 'string' or r_type == 'string':
            if op != '+':
                panic('Invalid operator {} between two strings.'.format(op))
            val = str(l_val) + str(r_val)
            typ = 'string'
            return (val, typ)
        if l_type == 'float' or r_type == 'float':
            if op == '%':
                panic(r'% cannot be applied to float type numbers.')
            conv = float
            typ = 'float'
        else:
            conv = int
            typ = 'int'

        if op == '+':
            val = conv(l_val) + conv(r_val)
        elif op == '-':
            val = conv(l_val) - conv(r_val)
        elif op == '*':
            val = conv(l_val) * conv(r_val)
        elif op == '/':
            val = conv(l_val) // conv(r_val) if typ == 'int' else conv(l_val) / conv(r_val)
        elif op == '%':
            val = conv(l_val) % conv(r_val)
        
        return (val, typ)

class Actions:
    # +++++ 基本翻译 ++++

    '''
    对数字的翻译
    '''
    @staticmethod
    def act_f_number(root, number):
        number_literal = number.token[1]
        if number_literal.find('.') == -1:
            val = int(number_literal)
            typ = 'int'
        else:
            val = float(number_literal)
            typ = 'float'
        root.set_attr('val', val)
        root.set_attr('type', typ)

    '''
    ID开头的节点，把token作为子节点的继承属性传下去
    '''
    @staticmethod
    def act_f_id_head(root, id, idsuf):
        yield (idsuf, {
            'token': id.token[1]
        })
        root.set_attr('val', idsuf.get_attr('val'))
        root.set_attr('type', idsuf.get_attr('type'))

    '''
    纯粹的ID，直接去符号表里查
    '''
    @staticmethod
    def act_idsuf_eps(root, eps, token):
        val = SymbolTable.get(token)
        root.set_attr('val', val[0])
        root.set_attr('type', val[1])

    '''
    对字符串的翻译
    '''
    @staticmethod
    def act_t_string(root, string):
        root.set_attr('val', string.token[1])
        root.set_attr('type', 'string')

    '''
    系统级的转换为整数的函数
    int(expr)
    '''
    @staticmethod
    def act_f_int(root, tint, lb, expr, rb):
        yield expr
        root.set_attr('val', int(expr.get_attr('val')))
        root.set_attr('type', 'int')

    '''
    数组的系统级初始化
    '''
    @staticmethod
    def act_f_array_init(root, token):
        root.set_attr('val', {})
        root.set_attr('type', 'array')

    # +++++ 表达式部分 ++++

    '''
    []符号
    数组名[整型表达式]
    '''
    @staticmethod
    def act_idsuf_arr(root, ld, first_param, rd, params, token):
        yield first_param
        param_list = [first_param.get_attr('val')]
        cur = params
        try:
            while cur.node_type != '_EPS':
                yield cur
                param_list.append(cur.children[1].get_attr('val'))
                cur = cur.children[3]
        except (IndexError, TypeError):
            pass
            
        value = SymbolTable.get(token)[0]
        for index in param_list:
            value = value[index]
    
        root.set_attr('val', value[0])
        root.set_attr('type', value[1])

    '''
    ()符号
    表达式
    '''
    @staticmethod
    def act_f_brackets(root, lb, child_e, rb):
        yield child_e
        root.set_attr('val', child_e.get_attr('val'))
        root.set_attr('type', child_e.get_attr('type'))

    '''
    ()符号
    函数名(形式参数表)
    '''
    @staticmethod
    def act_idsuf_func(root, lop, params, rop, token):
        param_list = []
        try:
            yield params.children[0]
            if params.children[0].node_type != '_EPS':
                param_list.append([params.children[0].get_attr('val'), params.children[0].get_attr('type')])
                cur = params.children[1]
                while len(cur.children) >= 3:
                    yield cur
                    param_list.append([cur.children[1].get_attr('val'), cur.children[1].get_attr('type')])
                    cur = cur.children[2]
        except (IndexError, TypeError):
            pass
        
        try:
            (func_name, func_root, vparams), typ = SymbolTable.get_with_error(token)
        except KeyError:
            # load from runtime lib
            try:
                target = getattr(RuntimeFunctions, 'function_{}'.format(token))
            except AttributeError:
                panic('Call to undefined function: {}'.format(token))
            
            return_value = target(**dict(zip(target.vparams, param_list)))
            root.set_attr('val', return_value[0])
            root.set_attr('type', return_value[1])
            return

        # load from symbol table
        SymbolTable.enter_scope()
        SymbolTable.get_current_scope_symbols_ref().update(dict(zip(vparams, param_list)))
        yield func_root
        try:
            return_value = SymbolTable.get_with_error(SYS_SYMBOL_PREFIX + 'retval')
            root.set_attr('val', return_value[0])
            root.set_attr('type', return_value[1])
        except KeyError:
            pass
        SymbolTable.leave_scope()

    '''
    各种运算表达式的汇合
    '''
    @staticmethod
    def act_e_suffix(root, lowest_priority_child):
        yield lowest_priority_child
        root.set_attr('val', lowest_priority_child.get_attr('val'))
        root.set_attr('type', lowest_priority_child.get_attr('type'))

    '''
    负号
    -表达式
    '''
    @staticmethod
    def act_f_negative_number(root, neg_token, number):
        yield number
        root.set_attr('val', -number.get_attr('val'))
        root.set_attr('type', number.get_attr('type'))

    '''
    非运算符
    !表达式
    '''
    @staticmethod
    def act_f_not(root, not_token, fact):
        yield fact
        root.set_attr('val', 0 if fact.get_attr('val') else 1)
        root.set_attr('type', 'int')

    '''
    乘法因子表达式
    '''
    @staticmethod
    def act_t_suffix(root, child_f, child_y):
        yield child_f
        yield (child_y, {
            'inh_val': child_f.get_attr('val'),
            'inh_type': child_f.get_attr('type')
        })
        root.set_attr('val', child_y.get_attr('syn_val'))
        root.set_attr('type', child_y.get_attr('syn_type'))

    '''
    乘法
    '''
    @staticmethod
    def act_y_prod_expr(root, child_token, child_f, child_y, inh_val, inh_type):
        yield child_f
        val, typ = Utils.binary_normal_calc('*', (inh_val, inh_type), (child_f.get_attr('val'), child_f.get_attr('type')))
        yield (child_y, {
            'inh_val': val,
            'inh_type': typ
        })
        root.set_attr('syn_val', child_y.get_attr('syn_val'))
        root.set_attr('syn_type', child_y.get_attr('syn_type'))

    '''
    除法
    '''
    @staticmethod
    def act_y_div_expr(root, child_token, child_f, child_y, inh_val, inh_type):
        yield child_f
        val, typ = Utils.binary_normal_calc('/', (inh_val, inh_type), (child_f.get_attr('val'), child_f.get_attr('type')))
        yield (child_y, {
            'inh_val': val,
            'inh_type': typ
        })
        root.set_attr('syn_val', child_y.get_attr('syn_val'))
        root.set_attr('syn_type', child_y.get_attr('syn_type'))

    '''
    模法
    '''
    @staticmethod
    def act_y_mod_expr(root, child_token, child_f, child_y, inh_val, inh_type):
        yield child_f
        val, typ = Utils.binary_normal_calc('%', (inh_val, inh_type), (child_f.get_attr('val'), child_f.get_attr('type')))
        yield (child_y, {
            'inh_val': val,
            'inh_type': typ
        })
        root.set_attr('syn_val', child_y.get_attr('syn_val'))
        root.set_attr('syn_type', child_y.get_attr('syn_type'))

    '''
    乘法因子计算结束，syn值需要逐级上传
    '''
    @staticmethod
    def act_y_eps(root, eps, inh_val, inh_type):
        root.set_attr('syn_val', inh_val)
        root.set_attr('syn_type', inh_type)

    '''
    加法因子表达式
    '''
    @staticmethod
    def act_sum_suffix(root, child_t, child_x):
        yield child_t
        yield (child_x, {
            'inh_val': child_t.get_attr('val'),
            'inh_type': child_t.get_attr('type')
        })
        root.set_attr('val', child_x.get_attr('syn_val'))
        root.set_attr('type', child_x.get_attr('syn_type'))

    '''
    加法
    '''
    @staticmethod
    def act_x_plus_expr(root, child_token, child_t, child_x, inh_val, inh_type):
        yield child_t
        val, typ = Utils.binary_normal_calc('+', (inh_val, inh_type), (child_t.get_attr('val'), child_t.get_attr('type')))
        yield (child_x, {
            'inh_val': val,
            'inh_type': typ
        })
        root.set_attr('syn_val', child_x.get_attr('syn_val'))
        root.set_attr('syn_type', child_x.get_attr('syn_type'))
    
    '''
    减法
    '''
    @staticmethod
    def act_x_sub_expr(root, child_token, child_t, child_x, inh_val, inh_type):
        yield child_t
        val, typ = Utils.binary_normal_calc('-', (inh_val, inh_type), (child_t.get_attr('val'), child_t.get_attr('type')))
        yield (child_x, {
            'inh_val': val,
            'inh_type': typ
        })
        root.set_attr('syn_val', child_x.get_attr('syn_val'))
        root.set_attr('syn_type', child_x.get_attr('syn_type'))

    '''
    加法因子计算结束，syn值需要逐级上传
    '''
    @staticmethod
    def act_x_eps(root, eps, inh_val, inh_type):
        root.set_attr('syn_val', inh_val)
        root.set_attr('syn_type', inh_type)

    '''
    比较符号
    '''
    @staticmethod
    def act_cmp_calc_val_suffix(root, sum, cmp_calc):
        yield sum
        yield (cmp_calc, {
            'inh_val': sum.get_attr('val'),
            'inh_type': sum.get_attr('type')
        })
        root.set_attr('val', cmp_calc.get_attr('syn_val'))
        root.set_attr('type', cmp_calc.get_attr('syn_type'))
    
    '''
    小于号
    '''
    @staticmethod
    def act_cmp_calc_lt(root, token, sum, cmp_calc, inh_val, inh_type):
        yield sum
        right_val = sum.get_attr('val')
        yield (cmp_calc, {
            'inh_val': 1 if inh_val < right_val else 0,
            'inh_type': 'int'
        })
        root.set_attr('syn_val', cmp_calc.get_attr('syn_val'))
        root.set_attr('syn_type', cmp_calc.get_attr('syn_type'))

    '''
    小于等于号
    '''
    @staticmethod
    def act_cmp_calc_lte(root, token, sum, cmp_calc, inh_val, inh_type):
        yield sum
        right_val = sum.get_attr('val')
        yield (cmp_calc, {
            'inh_val': 1 if inh_val <= right_val else 0,
            'inh_type': 'int'
        })
        root.set_attr('syn_val', cmp_calc.get_attr('syn_val'))
        root.set_attr('syn_type', cmp_calc.get_attr('syn_type'))

    '''
    大于号
    '''
    @staticmethod
    def act_cmp_calc_gt(root, token, sum, cmp_calc, inh_val, inh_type):
        yield sum
        right_val = sum.get_attr('val')
        yield (cmp_calc, {
            'inh_val': 1 if inh_val > right_val else 0,
            'inh_type': 'int'
        })
        root.set_attr('syn_val', cmp_calc.get_attr('syn_val'))
        root.set_attr('syn_type', cmp_calc.get_attr('syn_type'))

    '''
    比较等于号
    '''
    @staticmethod
    def act_cmp_calc_eq(root, token, sum, cmp_calc, inh_val, inh_type):
        yield sum
        right_val = sum.get_attr('val')
        yield (cmp_calc, {
            'inh_val': 1 if inh_val == right_val else 0,
            'inh_type': 'int'
        })
        root.set_attr('syn_val', cmp_calc.get_attr('syn_val'))
        root.set_attr('syn_type', cmp_calc.get_attr('syn_type'))

    '''
    不等于号
    '''
    @staticmethod
    def act_cmp_calc_neq(root, token, sum, cmp_calc, inh_val, inh_type):
        yield sum
        right_val = sum.get_attr('val')
        yield (cmp_calc, {
            'inh_val': 1 if inh_val != right_val else 0,
            'inh_type': 'int'
        })
        root.set_attr('syn_val', cmp_calc.get_attr('syn_val'))
        root.set_attr('syn_type', cmp_calc.get_attr('syn_type'))

    '''
    大于等于号
    '''
    @staticmethod
    def act_cmp_calc_gte(root, token, sum, cmp_calc, inh_val, inh_type):
        yield sum
        right_val = sum.get_attr('val')
        yield (cmp_calc, {
            'inh_val': 1 if inh_val >= right_val else 0,
            'inh_type': 'int'
        })
        root.set_attr('syn_val', cmp_calc.get_attr('syn_val'))
        root.set_attr('syn_type', cmp_calc.get_attr('syn_type'))

    '''
    比较符号计算结束，需要逐级上传
    '''
    @staticmethod
    def act_cmp_calc_eps(root, eps, inh_val, inh_type):
        root.set_attr('syn_val', inh_val)
        root.set_attr('syn_type', inh_type)

    '''
    逻辑运算符号
    '''
    @staticmethod
    def act_logic_calc_val_suffix(root, cmp_calc_val, logic_calc):
        yield cmp_calc_val
        yield (logic_calc, {
            'inh_val': cmp_calc_val.get_attr('val'),
            'inh_type': cmp_calc_val.get_attr('type')
        })
        root.set_attr('val', logic_calc.get_attr('syn_val'))
        root.set_attr('type', logic_calc.get_attr('syn_type'))

    '''
    逻辑与
    注意短路原则的使用
    '''
    @staticmethod
    def act_logic_calc_land_expr(root, token, val, calc, inh_val, inh_type):
        yield val
        right_val = val.get_attr('val')
        
        # 短路原则
        if not inh_val or not right_val:
            root.set_attr('syn_val', 0)
            root.set_attr('syn_type', 'int')
            return
        
        yield(calc, {
            'inh_val': 1,
            'inh_type': 'int'
        })
        root.set_attr('syn_val', calc.get_attr('syn_val'))
        root.set_attr('syn_type', calc.get_attr('syn_type'))

    '''
    逻辑或
    注意短路原则的使用
    '''
    @staticmethod
    def act_logic_calc_lor_expr(root, token, val, calc, inh_val, inh_type):
        yield val
        right_val = val.get_attr('val')
        
        # 短路原则
        if inh_val or right_val:
            root.set_attr('syn_val', 1)
            root.set_attr('syn_type', 'int')
            return
        
        yield(calc, {
            'inh_val': 0,
            'inh_type': 'int'
        })
        root.set_attr('syn_val', calc.get_attr('syn_val'))
        root.set_attr('syn_type', calc.get_attr('syn_type'))

    '''
    逻辑运算结束，逐级回传syn
    '''
    @staticmethod
    def act_logic_calc_eps(root, eps, inh_val, inh_type):
        root.set_attr('syn_val', inh_val)
        root.set_attr('syn_type', inh_type)

    # +++++ 语句部分 +++++

    '''
    语句
    '''
    @staticmethod
    def act_stmt_expr_stmt(root, expr, token, stmt):
        yield expr
        root.set_attr('val', expr.get_attr('val'))
        root.set_attr('type', expr.get_attr('type'))
        yield stmt

    '''
    赋值语句
    let a = expr
    '''
    @staticmethod
    def act_stmt_assign_stmt(root, let, assign, params, token, expr, dl, next_stmt):
        yield expr
        val = expr.get_attr('val')
        typ = expr.get_attr('type')
        root.set_attr('val', val)
        root.set_attr('type', typ)

        param_list = []
        cur = params
        try:
            while cur.node_type != '_EPS':
                yield cur
                param_list.append(cur.children[1].get_attr('val'))
                cur = cur.children[3]
        except (IndexError, TypeError):
            pass
        
        id = assign.token[1]
        if not len(param_list):
            SymbolTable.assign(id, [val, typ])
        else:
            ref = SymbolTable.get(id)[0]
            for index in param_list[:-1]:
                if index not in ref or not isinstance(ref[index], dict):
                    ref[index] = {}
                ref = ref[index]
            ref[param_list[-1]] = [val, typ]

        yield next_stmt

    '''
    系统级别的输出语句
    print(expr)
    '''
    @staticmethod
    def act_stmt_print_stmt(root, print_token, lb, expr, rb, spl, stmt):
        yield expr
        val = expr.get_attr('val')
        if expr.get_attr('type') == 'func':
            func_name, obj, params = val
            print('<Function {}({})>'.format(func_name, ', '.join(params)), end='')
        else:
            print(val, end='')
        yield stmt
    
    '''
    IF语句
    '''
    @staticmethod
    def act_stmt_if_stmt(root, token_if, expr, lb, stmt, rb, else_stmt, next_stmt):
        yield expr
        if expr.get_attr('val'):
            yield stmt
        else:
            yield else_stmt
        yield next_stmt
    
    '''
    ELSE子句
    '''
    @staticmethod
    def act_else_else(root, token_else, lb, stmt, rb):
        yield stmt
    
    '''
    WHILE语句
    '''
    @staticmethod
    def act_stmt_while_stmt(root, token_while, expr, lb, stmt, rb, next_stmt):
        while True:
            yield expr
            expr_value = expr.get_attr('val')
            if not expr_value:
                break
            yield stmt

        yield next_stmt

    '''
    LOOP语句
    '''
    @staticmethod
    def act_stmt_loop_stmt(root, token_for, id, token_from, num_from, token_to, num_to, lb, stmt, rb, next_stmt):
        yield num_from
        yield num_to

        name = id.token[1]
        
        ref = SymbolTable.assign(name, [int(num_from.get_attr('val')), 'int'])
        while ref[0] <= int(num_to.get_attr('val')):
            yield stmt
            ref[0] += 1
        
        yield next_stmt

    '''
    函数定义语句
    '''
    @staticmethod
    def act_stmt_func_stmt(root, func, id, lb, params, rb, lbb, func_root, rbb, next_stmt):
        param_list = []
        try:
            param_list.append(params.children[0].token[1])
            cur = params.children[1]
            while len(cur.children) >= 3:
                param_list.append(cur.children[1].token[1])
                cur = cur.children[2]
        except (IndexError, TypeError):
            pass
        
        SymbolTable.assign(id.token[1], [(id.token[1], func_root, param_list), 'func'])
        
        yield next_stmt

    '''
    return语句
    '''
    @staticmethod
    def act_stmt_ret_stmt(root, token_ret, expr, dm, next_stmt):
        yield expr
        SymbolTable.assign(SYS_SYMBOL_PREFIX + 'retval', [expr.get_attr('val'), expr.get_attr('type')])
        # do not execute next stmt

def simple_sdd(parse_tree, **kwargs):
    SDD_CALL_STACK.append(x for x in (parse_tree, ))

    while len(SDD_CALL_STACK):
        try:
            node = next(SDD_CALL_STACK[-1])
        except StopIteration:
            SDD_CALL_STACK.pop()
            continue

        kwargs = {}
        if isinstance(node, tuple):
            kwargs.update(node[1])
            node = node[0]

        if node.node_type != 'N':
            continue
        
        # if a function returns, terminate the sub procedure
        if SymbolTable.exists(SYS_SYMBOL_PREFIX + 'retval'):
            continue

        try:
            action = getattr(Actions, 'act_{}_{}'.format(node.symbol.lower(), node.production_name.lower()))
        except AttributeError as e:
            SDD_CALL_STACK.append(x for x in node.children)
            continue

        result_iter = action(*([node] + node.children), **kwargs)
        if isinstance(result_iter, GeneratorType):
            SDD_CALL_STACK.append(result_iter)

if __name__ == '__main__':
    ParseTree.build_parse_tree()
    parse_tree = ParseTree.get_parse_tree()
    simple_sdd(parse_tree)
