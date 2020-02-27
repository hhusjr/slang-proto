'''
语法分析树数据结构
'''
class ParseTree_Node:
    def __init__(self, node_type, token=None, symbol=None, production_name=None):
        self.children = []

        self.symbol = symbol
        self.production_name = production_name

        if node_type not in ('T', 'N', '_EPS'):
            raise ValueError
        self.node_type = node_type

        if token is not None:
            if not isinstance(token, tuple) or len(token) < 1:
                raise TypeError
            self.token = token
        else:
            self.token = None
        
        self.attrs = {}

    def set_attr(self, attr, value):
        self.attrs[attr] = value
    
    def get_attr(self, attr):
        try:
            return self.attrs[attr]
        except KeyError:
            return None
    
    def add_child(self, child):
        if not isinstance(child, ParseTree_Node):
            raise TypeError
        self.children.append(child)

    # DEBUGGING & TESTING

    def get_node_text(self, node):
        attrs_str = str(node.attrs)
        if node.node_type == 'T':
            return '{}[{}]'.format(node.token[0], attrs_str)
        if node.node_type == 'N':
            return '{}[{}]'.format(node.symbol, attrs_str)
        return '{}[{}]'.format('_EPS', attrs_str)

    def _print_tree(self, root):
        if not len(root.children):
            return
        formatted_text = '{} ::== '.format(self.get_node_text(root))
        for child in root.children:
            formatted_text += '{} '.format(self.get_node_text(child))
        print(formatted_text)
        for child in root.children:
            self._print_tree(child)

    def print_tree(self):
        self._print_tree(self)