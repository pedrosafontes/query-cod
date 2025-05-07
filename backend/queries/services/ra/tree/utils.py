def text(text: str) -> str:
    return f'\\text{{{text}}}'


def subscript(expr: str, subscript: str) -> str:
    return f'{expr}_{{{subscript}}}'


def overset(overset: str, expr: str) -> str:
    return f'\\overset{{{overset}}}{{{expr}}}'


PI = '\\pi'
SIGMA = '\\sigma'
GAMMA = '\\Gamma'
CUP = '\\cup'
CAP = '\\cap'
JOIN = '\\Join'
LTIMES = '\\ltimes'
DIV = '\\div'
LAND = '\\land'
LOR = '\\lor'
LNOT = '\\lnot'
NEQ = '\\neq'
LEQ = '\\leq'
GEQ = '\\geq'
