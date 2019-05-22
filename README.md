# role-pattern

For building and matching token patterns in text where we want to assign tokens to roles. For example:

"Forging involves the shaping of metal using localized compressive forces."

arg1: [Forging]
pred: [involves]
arg2: [shaping]

head: [shaping]
prep-tail: [of metal]

arg1: [shaping]
pred: [using]
arg2: [localized compressive forces]

## Built with

This approach uses graph-based pattern matching, built on SpaCy. Patterns are built from training examples using spacy-dependency-pattern-builder. Matches are found using SpaCy's DependencyTreeMatcher. The RolePattern class provides a layer over those components to handle the role assignment and plumbing.

## Usage

import role_pattern

text = "Forging involves the shaping of metal using localized compressive forces."

doc = nlp(text)

def idxs_to_tokens(idxs):
    return [doc[idx] for idx in idxs]

match_example = {
    arg1:
    pred:
    arg2:
}

pattern = role_pattern.build(doc, match_example)

print(pattern)

matches = pattern.find_matches(doc)

