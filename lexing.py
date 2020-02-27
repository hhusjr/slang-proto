from src_code import SourceCode
import sys

EOF = ('$', '$')

RESERVED_WORDS = (
    'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if',
    'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof', 'static', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'void',
    'volatile', 'while',
    # do some diy here
    'print', 'to', 'from', 'loop', 'ref', 'func', 'ret', 'let', 'Array'
)
ESCAPE_CHARACTER_MAPPING = {
    'a': chr(7),
    'b': chr(8),
    'f': chr(12),
    'n': chr(10),
    'r': chr(13),
    't': chr(9),
    'v': chr(11),
    '\'': chr(39),
    '"': chr(34),
    '\\': chr(92)
}
QUOTE_LITERAL_NAME = {
    '\'': 'CHAR_LITERAL',
    '"': 'STRING_LITERAL'
}
BASIC_OPERATOR_NAME = {
    '+': 'PLUS',
    '-': 'SUB',
    '*': 'PROD',
    '/': 'DIV',
    '&': 'AND',
    '|': 'OR',
    '^': 'XOR',
    '!': 'NOT',
    '=': 'EQ'
}
BASIC_OPERATOR_NAME_CP = {
    '>': 'GT',
    '<': 'LT',
    '>>': 'SHR',
    '<<': 'SHL'
}

def panic(msg):
    print('Lexing failed: {}'.format(msg))
    print('Parser failed, exiting...')
    sys.exit()

'''
空字符的判定
'''
def is_empty(x):
    return not x.strip()

'''
所有标识符/保留字都先当作标识符处理
然后判断是否为真正的标识符，或保留字
'''
def get_hypothetical_id_name(hypothetical_id):
    if hypothetical_id in RESERVED_WORDS:
        return hypothetical_id.upper()
    return 'ID'

'''
Token流的生成
'''
class TokenStream:
    _tokens = []
    _pointer = 0

    '''
    词法分析核心
    '''
    @staticmethod
    def tokenize():
        code = SourceCode.read_src_code()
        ch = next(code)
        tokens = TokenStream._tokens
        while ch is not None:
            # if ch is empty character
            if ch is not None and is_empty(ch):
                ch = next(code)
                continue

            # if ch is alpha a-z A-Z, consider identifier
            if ch is not None and ch.isalpha():
                identifier = ""
                while ch is not None and (ch.isalpha() or ch.isdigit() or ch == '_'):
                    identifier += ch
                    ch = next(code)
                tokens.append((get_hypothetical_id_name(identifier), identifier))
                continue

            # if ch is ' or ""
            if ch == '\'' or ch == '"':
                quote = ch
                literal = ''
                ch = next(code)
                while ch != quote:
                    literal += ch if ch != '\\' else ESCAPE_CHARACTER_MAPPING[next(code)]
                    ch = next(code)
                ch = next(code)
                tokens.append((QUOTE_LITERAL_NAME[quote], literal))
                continue

            # if ch is number, consider it as a number literal
            # num，numUL，numULL，numLL，numU，numF，numLF
            if ch is not None and ch.isdigit():
                literal = ''
                # number base
                while ch is not None and (ch.isdigit() or ch == '.'):
                    literal += ch
                    ch = next(code)
                tokens.append(('NUMBER_LITERAL', literal))
                continue

            # single character
            if ch in ('~', '%', '(', ')', '[', ']', '{', '}', ':', ';', '?', ','):
                tokens.append((ch, ))
                ch = next(code)
                continue

            # + - * / ^ & | !
            if ch in BASIC_OPERATOR_NAME.keys():
                next_ch = next(code)
                name = BASIC_OPERATOR_NAME[ch]
                if next_ch == '=':
                    if ch != '=':
                        tokens.append((name + '_ASSIGN' if ch != '!' else 'NEQ', ))
                    else:
                        tokens.append(('IS_EQ', ))
                    ch = next(code)
                    continue
                if ch in ('+', '-') and next_ch == ch:
                    tokens.append((name + '_SELFOPT', ))
                    ch = next(code)
                    continue
                if ch in ('&', '|') and next_ch == ch:
                    tokens.append((name + 'L', ))
                    ch = next(code)
                    continue
                tokens.append((name, ))
                ch = next_ch
                continue

            # > < >> <<
            if ch in ('>', '<'):
                next_ch = next(code)
                name = BASIC_OPERATOR_NAME_CP[ch]
                if next_ch == '=':
                    tokens.append((name + 'E', ))
                    ch = next(code)
                    continue
                if next_ch == ch:
                    tmp = ch + next_ch
                    tokens.append((BASIC_OPERATOR_NAME_CP[tmp], ))
                    ch = next(code)
                    continue
                tokens.append((name, ))
                ch = next_ch
                continue
                
            panic('Invalid character {}'.format(ch))
    
    '''
    是否已经扫描完成
    '''
    @staticmethod
    def is_finished():
        return TokenStream._pointer >= len(TokenStream._tokens)

    '''
    获取所有token
    '''
    @staticmethod
    def get_tokens():
        return TokenStream._tokens

    '''
    获取下一个token
    '''
    @staticmethod
    def next():
        try:
            token = TokenStream._tokens[TokenStream._pointer]
        except IndexError:
            return EOF
        TokenStream._pointer += 1
        return token
    

    '''
    获取向前看的值
    '''
    @staticmethod
    def get_look_ahead():
        try:
            token = TokenStream._tokens[TokenStream._pointer]
        except IndexError:
            return EOF
        return token
    
    '''
    获取指针位置
    '''
    @staticmethod
    def get_pointer():
        return TokenStream._pointer

    '''
    设定指针位置
    '''
    @staticmethod
    def set_pointer(pos):
        TokenStream._pointer = pos

TokenStream.tokenize()

# For testing
if __name__ == '__main__':
    tokens = TokenStream.get_tokens()
    for token in tokens:
        print(token)