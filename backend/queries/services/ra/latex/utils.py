def text(text: str) -> str:
    replacements = {
        '\\': r'\\textbackslash{}',
        '{': r'\{',
        '}': r'\}',
        '_': r'\_',
        '^': r'\^{}',
        '#': r'\#',
        '$': r'\$',
        '%': r'\%',
        '&': r'\&',
        '~': r'\\textasciitilde{}',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return f'\\text{{{text}}}'


def subscript(base: str, sub: str) -> str:
    return f'{base}_{{{sub}}}'


def paren(content: str) -> str:
    return f'({content})'


def overset(top: str, bottom: str) -> str:
    return f'\\overset{{{top}}}{{{bottom}}}'


AND = '\\land'
OR = '\\lor'
NOT = '\\lnot'
NEQ = '\\neq'
LEQ = '\\leq'
GEQ = '\\geq'
PI = '\\pi'
SIGMA = '\\sigma'
RHO = '\\rho'
CUP = '\\cup'
CAP = '\\cap'
TIMES = '\\times'
JOIN = '\\Join'
LTIMES = '\\ltimes'
ANTIJOIN = '\\overline{\\Join}'
LEFTJOIN = '⟕'
RIGHTJOIN = '⟖'
OUTERJOIN = '⟗'
BOWTIE = '\\bowtie'
DIV = '\\div'
TOP_N = '\\operatorname{T}'
GAMMA = '\\Gamma'
