from grammars import GRAMMARS

class GrammarHelper:
    N = set()
    T = set()
    P = set()
    ALL = set()

    @staticmethod
    def get():
        for (lhs, rhs) in GRAMMARS.items():
            GrammarHelper.N.add(('N', lhs))
            GrammarHelper.ALL.add(('N', lhs))
            for (name, production) in rhs.items():
                GrammarHelper.P.add((('N', lhs), (name, production)))
                for element in production:
                    node_type, name = element
                    # N/T
                    if node_type == 'N':
                        GrammarHelper.N.add(element)
                    elif node_type == 'T':
                        GrammarHelper.T.add(element)
                    GrammarHelper.ALL.add(element)
    
    @staticmethod
    def get_productions_with(element):
        for (lhs, rhs) in GRAMMARS.items():
            for (name, production) in rhs.items():
                for (index, el) in enumerate(production):
                    if element != el:
                        continue
                    follow_el = production[index + 1] if index < len(production) - 1 else None
                    yield (('N', lhs), (name, production), follow_el)

GrammarHelper.get()