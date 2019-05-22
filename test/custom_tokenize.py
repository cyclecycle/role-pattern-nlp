from pprint import pprint
import re
from spacy.tokenizer import Tokenizer
from spacy.util import compile_prefix_regex, compile_infix_regex, compile_suffix_regex
from spacy.attrs import ORTH, LEMMA, TAG


prefixes = [r'\((?=[^\)]+$)']

def custom_tokenizer(nlp):
    prefix_re = compile_prefix_regex(prefixes)
    suffix_re = compile_suffix_regex(nlp.Defaults.suffixes)

    rules = {
        'chromatography': [{
            ORTH: 'chromatography', LEMMA: 'chromatography', TAG: 'NN'
        }],
        'knockdown': [{
            ORTH: 'knockdown', LEMMA: 'knockdown', TAG: 'NN'
        }]
    }

    return Tokenizer(nlp.vocab, rules=rules,
                     prefix_search=prefix_re.search,
                     suffix_search=suffix_re.search,
                     # infix_finditer=infix_re.finditer,
                     token_match=None)


if __name__ == '__main__':

    import spacy

    nlp = spacy.load('en')

    text = """
    The purification procedure included fractionation with (NH1)2SO1, 
    heat treatment, DEAE-cellulose chromatography and hydroxyapatite chromatography.
    """

    text = text.replace('\n', '')

    nlp.tokenizer = custom_tokenizer(nlp)

    doc = nlp(text)
    pprint([token.text for token in doc])