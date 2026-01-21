import nltk
from nltk import CFG
from nltk.parse import ChartParser

# —————————————————————————————————————————————————————————————
# Gramática G₂ (sin ambigüedad ni recursividad izquierda) en NLTK
# —————————————————————————————————————————————————————————————
hausa_grammar_unambiguous = CFG.fromstring(r"""
S         -> NP VP

NP        -> N NP_Aux
NP_Aux    -> 'da' N NP_Aux
NP_Aux    ->

VP        -> V VP_Tail
VP_Tail   -> NP
VP_Tail   ->

N         -> 'mutum' | 'yara' | 'zomo' | 'kare'
V         -> 'suna'  | 'hauji' | 'ganowa'
""")

parser = ChartParser(hausa_grammar_unambiguous)

test_sentences = [
    "mutum da zomo da kare ganowa yara",
    "mutum da yara suna",
    "zomo ganowa yara",
]

for sentence in test_sentences:
    tokens = sentence.split()
    trees = list(parser.parse(tokens))
    print(f"'{sentence}' genera {len(trees)} árbol(es):")
    for tree in trees:
        tree.pretty_print()
    print()