import en_core_web_sm
text = "Forging involves the shaping of metal using localized compressive forces."
nlp = en_core_web_sm.load()
doc = nlp(text)

from role_pattern_nlp import RolePatternBuilder

def idxs_to_tokens(idxs):
    return [doc[idx] for idx in idxs]

match_example = {
    arg1: idxs_to_tokens(idx, [0]),
    pred: idxs_to_tokens(idx, [1]),
    arg2: idxs_to_tokens(idx, [3]),
}

pattern = role_pattern.build(doc, match_example)

print(pattern)

matches = pattern.find_matches(doc)